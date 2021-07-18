
# WordpPress ThemeREX Addons 插件安全漏洞深度分析


                                阅读量   
                                **532903**
                            
                        |
                        
                                                                                    



[![](./img/201296/t01c55bb061cab33df3.png)](./img/201296/t01c55bb061cab33df3.png)



## 0x00 前言

ThemeREX是一家专门出售商业WordPress主题的公司。ThemeREX<br>
Addons插件为ThemeREX公司开发的预装在所有ThemeREX商业主题中用来帮助其用户设置新站点和控制不同的主题的一款插件。根据相关预测，该插件预装在超过44000个网站上。

[![](./img/201296/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/03/19/8rvrSf.png)



## 0x01 漏洞描述

WordPress ThemeREX Addons<br>
2020-03-09之前版本中存在安全漏洞。未经授权的攻击者可利用该漏洞在后台添加一个管理员账号、或是查看所有账号信息等操作。



## 0x02 漏洞分析

根据相关披露，漏洞应该存在于plugin.rest-api.php文件中

我们首先来看一下wp-contentpluginstrx_addonsincludesplugin.rest-api.php文件中的代码

位于该文件40行处，存在一处trx_addons_rest_get_sc_layout方法，如下图

[![](./img/201296/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/03/19/8rv0Yt.png)

在该方法中，存在一处明显的漏洞点，见下图代码块

[![](./img/201296/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/03/19/8rvsl8.png)

接下来我们根据这段代码详细分析下。我们首先来观察一下下图53行红框处

[![](./img/201296/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/03/19/8rvy6S.png)

位于上图红框处，可见程序从请求中直接获得参数，并将请求中的参数键值对赋值与$params数组。这将导致$params数组可控

紧接着，程序判断$params数组中是否存在名为’sc’的键名，见下图红框处

[![](./img/201296/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/03/19/8rv8SK.png)

若该键名存在，经过字符替换处理后将其值赋与$sc变量。

简单来说，这里的$sc变量可以通过请求中的sc参数进行传递。

随后，程序通过function_exists判断$sc变量对应的方法是否存在，见下图

[![](./img/201296/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/03/19/8rvaTA.png)

如果$sc变量中对应的方法存在，程序将$params数组作为参数列表传入该方法执行。

至此，漏洞的触发点我们已经分析完毕。接下来我们需要寻找一下调用链

由于漏洞触发点位于trx_addons_rest_get_sc_layout方法中，我们需要分析一下如何构造请求以触发这个漏洞。

仍然是位于wp-contentpluginstrx_addonsincludesplugin.rest-api.php文件中，有着如下代码

[![](./img/201296/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/03/19/8rveL4.png)

通过上图可见，程序通过add_action方法将trx_addons_rest_register_endpoints函数挂接到rest_api_init动作上。

我们查看一下rest_api_init这个动作

[![](./img/201296/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/03/19/8rvkWV.png)

通过上图描述不难看出：<br>
rest_api_init动作将会在API请求发送到服务器后，服务器初始化处理API请求时触发。将trx_addons_rest_register_endpoints函数挂接到rest_api_init动作上，当有API请求发送到后台处理时，trx_addons_rest_register_endpoints方法将会被加载。

继续跟踪后续代码

[![](./img/201296/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/03/19/8rvRTs.png)

在trx_addons_rest_register_endpoints方法中通过register_rest_route方法注册了一个自定义接口，见上图红框处。

这里简单介绍一下register_rest_route方法：

WordPress官方核心代码提供了一套WP_REST_API接口，但是实际开发以及使用过程中难免会出现官方API接口满足不了实际需求的状况。为此WordPress提供了register_rest_route方法用于自定义注册WP<br>
REST API接口。

register_rest_route方法参数如下

[![](./img/201296/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/03/19/8rvfkn.png)

在介绍完register_rest_route方法后，我们回归漏洞代码，分析此处register_rest_route方法注册的API接口

[![](./img/201296/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/03/19/8rvQF1.png)

通过上图第一个红框处namespace以及route属性值可知：该接口路由为trx_addons/v2/get/sc_layout；通过第二个红框methods属性值可知：该接口可以通过GETPOST方法访问；通过第三个红框callback属性值可知：该接口回调函数为漏洞触发点trx_addons_rest_get_sc_layout方法。通过上述信息，我们可以构造出通往漏洞触发点的请求。

除了通过分析代码来请求这种方法外，我们还可以通过wordpress还提供的接口来方便快捷的查看所有注册的API接口信息。

访问127.0.0.1/wordpress/wp-json/ 见下图

[![](./img/201296/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/03/19/8rvJyD.png)

wp-json这个目录会将wordpress中所有注册的API接口信息展示出来。

通过页面中展示的API列表，我们可以看见/trx_addons/v2/get/sc_layout路由信息

展开/trx_addons/v2/get/sc_layout路由 见下图

[![](./img/201296/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/03/19/8rv2wj.png)

上图为展开后的详细接口信息，在这里我们可以看到该接口允许的methods以及url地址

值得注意的是：通过分析 /trx_addons/v2/get/sc_layout接口代码时可发现，ThemeREX<br>
Addons插件并没有在代码中使用current_user_can等方法对接口进行权限校验。也就是说，未经身份验证的用户也可以访问该接口从而触发漏洞



## 0x03 漏洞利用

通过上文的分析可知，我们可以通过请求来控制待执行的函数名，并可以通过一个数组对该函数传参。因此我们需要找到一个可以利用的PHP或wordpress函数，该函数需要满足可以接收并处理数组类型参数

### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E4%B8%80%EF%BC%9A%E9%80%9A%E8%BF%87wp_insert_user%E6%96%B0%E5%BB%BA%E7%AE%A1%E7%90%86%E5%91%98%E8%B4%A6%E5%8F%B7"></a>利用一：通过wp_insert_user新建管理员账号

构造如下链接：

[http://127.0.0.1/wordpress/?rest_route=/trx_addons/v2/get/sc_layout&amp;sc=wp_insert_user&amp;role=administrator&amp;user_login=TEST&amp;user_pass=TEST](http://127.0.0.1/wordpress/?rest_route=/trx_addons/v2/get/sc_layout&amp;sc=wp_insert_user&amp;role=administrator&amp;user_login=TEST&amp;user_pass=TEST)

不需要进行登录操作，直接访问以上链接即可成功利用。

根据上文漏洞分析一章可知，该链接最终会触发trx_addons_rest_get_sc_layout方法，见下图

[![](./img/201296/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/03/19/8rvAzT.png)

此时上图中的$sc参数值对应payload中sc值，为wp_insert_user

此时$params数组值如下图

[![](./img/201296/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/03/19/8rvlJx.png)

程序将$params数组作为参数传入wp_insert_user方法并执行wp_insert_user方法。

wp_insert_user方法可以为wordpress程序添加一个指定权限的用户，该方法接收一个数组作为参数满足触发漏洞的要求，见下图

[![](./img/201296/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/03/19/8rvVQU.png)

wp_insert_user方法参数说明如下

[![](./img/201296/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/03/19/8rvYOe.png)

由此一来，wordpress中将会增添一个administrator权限的名为TEST的用户，如下图

[![](./img/201296/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/03/19/8rvuw9.png)

利用新创建的管理员账号可以完成进一步攻击：例如通过修改wordpress模板等操作，在wordpress中写入后门文件。

### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E4%BA%8C%EF%BC%9A%E9%80%9A%E8%BF%87wp_dropdown_users%E6%9F%A5%E7%9C%8B%E6%89%80%E6%9C%89%E8%B4%A6%E5%8F%B7%E4%BF%A1%E6%81%AF"></a>利用二：通过wp_dropdown_users查看所有账号信息

构造如下链接：

[http://127.0.0.1/wordpress/wp-json/trx_addons/v2/get/sc_layout?sc=wp_dropdown_users&amp;show=user_login](http://127.0.0.1/wordpress/wp-json/trx_addons/v2/get/sc_layout?sc=wp_dropdown_users&amp;show=user_login)

wp_dropdown_users为wordpress提供的用来查询用户信息的函数

[![](./img/201296/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/03/19/8rvUwd.png)

wp_dropdown_users同样满足可以接收一个数组作为参数的需求，wp_dropdown_users参数说明如下

[![](./img/201296/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/03/19/8rv1W6.png)

通过wp_dropdown_users接口可以泄露wordpress账号信息。该操作同样不需要任何权限

上述payload中指定show参数值为user_login，这样可以查看wordpress所有用户名，见下图

[![](./img/201296/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/03/19/8rvNeH.png)

show参数值可以设置为user_pass来进行查看存储在数据库中加密后的密码，见下图

[![](./img/201296/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/03/19/8rvwFI.png)

show参数值可以设置为user_email来进行查看邮箱，见下图

[![](./img/201296/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/03/19/8rvGQO.png)‘

## 0x04 总结

为了解决安全问题，ThemeREX选择将受影响的plugin.rest-api.php文件完全删除。plugin.rest-api.php文件是为了提供与Gutenberg插件的兼容性而设计，但在目前版本中Gutenberg插件已完全集成为WordPress核心。因此plugin.rest-api.php文件不再被需要，删除该文件不会影响到用户的正常使用。

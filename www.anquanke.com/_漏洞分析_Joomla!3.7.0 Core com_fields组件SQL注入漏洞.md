> 原文链接: https://www.anquanke.com//post/id/86130 


# 【漏洞分析】Joomla!3.7.0 Core com_fields组件SQL注入漏洞


                                阅读量   
                                **115384**
                            
                        |
                        
                                                                                    



**[![](https://p0.ssl.qhimg.com/t018a33b26658facff4.jpg)](https://p0.ssl.qhimg.com/t018a33b26658facff4.jpg)**

**<br>**



**传送门**

**[【漏洞预警】Joomla!3.7.0 Core SQL注入漏洞(更新漏洞环境)](http://bobao.360.cn/learning/detail/3868.html)**

[**【漏洞分析】Joomla!3.7.0 Core SQL注入漏洞详细分析（含PoC、漏洞环境）******](http://bobao.360.cn/learning/detail/3870.html)

**<br>**

**0x00 背景介绍**

Joomla!是一套全球知名的内容管理系统。Joomla!是使用PHP语言加上MySQL数据库所开发的软件系统，可以在Linux、 Windows、MacOSX等各种不同的平台上执行。目前是由Open Source Matters（见扩展阅读）这个开放源码组织进行开发与支持，这个组织的成员来自全世界各地，小组成员约有150人，包含了开发者、设计者、系统管理者、文件撰写者，以及超过2万名的参与会员。

<br>

**0x01 漏洞简介**

**漏洞名称：**Joomla!3.7.0 Core com_fields组件SQL注入漏洞

**漏洞分类：**SQL注入漏洞

**漏洞等级：**危急

**利用方式：**远程

**利用难度：**简单

**漏洞描述：**本漏洞出现在3.7.0新引入的一个组件“com_fields”，这个组件任何人都可以访问，无需登陆验证。由于对请求数据过滤不严导致sql注入，sql注入对导致数据库中的敏感信息泄漏。

**漏洞危害：**被SQL注入后可能导致以下后果：1.网页被篡改;2.数据被篡改;3.核心数据被窃取;4.数据库所在服务器被攻击变成傀儡主机

<br>

**0x02 漏洞流程图**

如果不想看下一部分的复杂分析，你只需要记住这个最简要的流程即可

[![](https://p2.ssl.qhimg.com/t01179b7a4ca1f32fad.png)](https://p2.ssl.qhimg.com/t01179b7a4ca1f32fad.png)

<br>

**0x03 漏洞分析**

从数据流层面分析下这个漏洞,网上流传的POC如下： /index.php?option=com_fields&amp;view=fields&amp;layout=modal&amp;list[fullordering]=updatexml(1,concat(0x3e,user()),0) 只从POC上可以看出list[fullordering]这个参数的值是经典的MYSQL报错语句，成功爆出了数据库用户信息，效果如图1所示： 

[![](https://p1.ssl.qhimg.com/t014bec168bafa55f15.png)](https://p1.ssl.qhimg.com/t014bec168bafa55f15.png)

图1

下面动态调试跟踪下本漏洞的成因，在这之前先讲下整个数据流的流程:

1. 入口点是C:phpStudy32WWWJoomla_3.7.0-Stable-Full_Packagecomponentscom_fieldscontroller.php，

public function __construct($config = array()) 方法获取传入的view、layout的值进行逻辑判断,给base_path赋值，如图2

[![](https://p0.ssl.qhimg.com/t01054dd39ea1e23fed.png)](https://p0.ssl.qhimg.com/t01054dd39ea1e23fed.png)

图2

parent::__construct($config); 这个构造方法将图3中几个参数进行赋值，赋值之后

的效果如图4所示:

[![](https://p3.ssl.qhimg.com/t0172bbfff1c5dc84e2.png)](https://p3.ssl.qhimg.com/t0172bbfff1c5dc84e2.png)

图3 

[![](https://p3.ssl.qhimg.com/t01abbbdf213d551b91.png)](https://p3.ssl.qhimg.com/t01abbbdf213d551b91.png)

图4

这个漏洞最核心的地方是list[fullordering]这个参数如何进行数据传递的！！！libraries/legacy/model/list.php这个文件中getUserStateFromRequest方法，它将url中的list[fullordering]值提取进行保存，如图5。

[![](https://p5.ssl.qhimg.com/t01c0a504b5004e2f0f.png)](https://p5.ssl.qhimg.com/t01c0a504b5004e2f0f.png)

 图5

经过对于fullordering值得简单判断，并没有做值的白名单校验，程序即将进入第一部分的关键也就是通过566行的$this-&gt;setState('list.' . $name, $value);方法保存我们的SQL注入报错代码进入list.fullordering保存的前后过程如图6，7所示。

[![](https://p5.ssl.qhimg.com/t01f288b53d5f1cb7c9.png)](https://p5.ssl.qhimg.com/t01f288b53d5f1cb7c9.png)

图6

[![](https://p1.ssl.qhimg.com/t01f90df161d0dde0f9.png)](https://p1.ssl.qhimg.com/t01f90df161d0dde0f9.png)

图7

1.	第一部分将我们的payload存进list.fullordering中，那么如何获取呢？直接进入最关键的部分./administrator/components/com_fields/models/fields.php文件中$listOrdering = $this-&gt;getState('list.fullordering', 'a.ordering');getState方法获取了之前保存的list.fullordering的值，如图8，并进行SQL语句的拼接，escape方法并没有把我们的payload过滤掉。

[![](https://p2.ssl.qhimg.com/t01a32b3de90ac039b7.png)](https://p2.ssl.qhimg.com/t01a32b3de90ac039b7.png)

图8

3.最后一步，执行SQL语句，拼接的语句完整语句如图9所示，在图9中也能看到报错的信息已经泄露，我们的payload已经成功执行了。

[![](https://p1.ssl.qhimg.com/t0191e26fb3bee62bcf.png)](https://p1.ssl.qhimg.com/t0191e26fb3bee62bcf.png)

图9

最终报错的信息输出到返回页面中，如图10所示。

[![](https://p3.ssl.qhimg.com/t01e33d107fb9e29072.png)](https://p3.ssl.qhimg.com/t01e33d107fb9e29072.png)

图10

完成的漏洞利用流程就走完了，下面对于这个漏洞的补丁进行分析。

<br>

**0x04 补丁分析**

[![](https://p1.ssl.qhimg.com/t017ce10806246c0d33.png)](https://p1.ssl.qhimg.com/t017ce10806246c0d33.png)

最版本中不获取用户可控的list.fullordering值了，改为获取list.ordering的值，那么这个POC改为：/index.php?option=com_fields&amp;view=fields&amp;layout=modal&amp;list[ordering]=updatexml(1,concat(0x3e,user()),0)

 	行不行呢？如下图进行的尝试，执行攻击失败。

[![](https://p0.ssl.qhimg.com/t010448b16d49f249fc.png)](https://p0.ssl.qhimg.com/t010448b16d49f249fc.png)

原因是在存list[ordering]状态的时候，ordering的检测逻辑是对于值进行了白名单的确认，如果值不在filter_fields数组中，那么list.ordering会被赋值为a.ordering,而不是之前我们的payload，如下图所示。 

[![](https://p0.ssl.qhimg.com/t013c57fbb1342adfa2.png)](https://p0.ssl.qhimg.com/t013c57fbb1342adfa2.png)

<br>

**0x05 总结**

这个漏洞是由于list[fullordering]参数用户可控，后端代码并没有进行有效过滤导致SQL语句拼接形成order by的注入，修复方案是执行语句获取list.ordering值进行了白名单过滤，在存储状态的时候就将攻击代码覆盖了，那么在执行语句之前取的值自然就不包含攻击代码了。

<br>

**0x06 参考**

[https://blog.sucuri.net/2017/05/sql-injection-vulnerability-joomla-3-7.html](https://blog.sucuri.net/2017/05/sql-injection-vulnerability-joomla-3-7.html) 

[https://github.com/joomla/joomla-cms](https://github.com/joomla/joomla-cms)    

<br>



**传送门**

**[【漏洞预警】Joomla!3.7.0 Core SQL注入漏洞(更新漏洞环境)](http://bobao.360.cn/learning/detail/3868.html)**

[**【漏洞分析】Joomla!3.7.0 Core SQL注入漏洞详细分析（含PoC、漏洞环境）**](http://bobao.360.cn/learning/detail/3870.html)

<br>

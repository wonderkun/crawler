
# 代码审计——Semcms


                                阅读量   
                                **319456**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](./img/203765/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](./img/203765/t01fdb3be42d250462b.jpg)](./img/203765/t01fdb3be42d250462b.jpg)



## 前言

这是我审计的第一个CMS，由于这次代码审计的初衷只是为了学习代码审计中寻找SQL注入的思路及大致流程，所以这次审计仅针对SQL注入



## 相关环境

源码信息 :semcms php 版外贸网站 V3.9<br>
本地环境 : phpstudy2014、seay代码审计工具<br>
cms官网地址 : [http://www.sem-cms.com/](http://www.sem-cms.com/)<br>
下载地址 : [http://ahdx.down.chinaz.com/201906/semcms_php_v3.9.zip](http://ahdx.down.chinaz.com/201906/semcms_php_v3.9.zip)



## 思路总结

分析项目结构，分析配置文件，<br>
根据统一过滤存在的绕过问题，遗漏的变量进行代码审计<br>
SQL语句中变量没用单引号闭合的都可能绕过<br>
对项目结构要有了解，要有一定代码功底



## 审计前的分析

### <a class="reference-link" name="%E4%B8%80%E3%80%81%E9%A1%B9%E7%9B%AE%E7%BB%93%E6%9E%84%E5%88%86%E6%9E%90"></a>一、项目结构分析

[![](./img/203765/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0155a553688e7fabcd.png)

/A_Admin为后台文件<br>
/Edit保存的是js文件和html文件<br>
/Image保存的是图片<br>
/include是包含全局的文件，有函数定义的文件，数据库配置，统一过滤配置文件<br>
/install是安装文件<br>
/Templete是一些js文件和一些图片

### <a class="reference-link" name="%E4%BA%8C%E3%80%81%E8%BF%87%E6%BB%A4%E4%BB%A3%E7%A0%81%E5%88%86%E6%9E%90"></a>二、过滤代码分析

#### <a class="reference-link" name="verify_str()%E5%87%BD%E6%95%B0%E5%88%86%E6%9E%90"></a>verify_str()函数分析

在文件/Include/contorl.php的第5行-第26行中将所有GET请求中的传参过滤，同时定义了verify_str()函数，当调用这个函数时，会对字符串进行正则匹配，当匹配成功时，执行exit()

1，调用了verify_strin()时(注入时不能用子查询(union select))<br>
2，不能有单引号(当SQL的变量包被单引号括起来时不能用单引号闭合<br>
3，不能有**号(不能用/***/注释绕过空格)<br>
4，不能用load_file，dnslog注入

[![](./img/203765/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01aa38426d1d6d7b75.png)

#### <a class="reference-link" name="test_input()%E5%87%BD%E6%95%B0%E5%88%86%E6%9E%90"></a>test_input()函数分析

第二处过滤位于 /semcms_php_v3.9/Include/contorl.php的第172行-177行，定义了一个名为test_input()的函数，当被调用时数据会被进行过滤

1，将字符串中的”%”替换为percent<br>
2，trim()函数，规定删除字符串中哪些函数，如果没有规定，则默认删除”″(NULL),”t”(制表符),”n”(换行),”xb”(垂直制表符),”r”(回车),” “(空格)<br>
3，stripslashes()删除反斜杠(不能使用反斜杠””转义SQL语句中的单引号或双引号)<br>
4，特殊字符html实体化，ENT_QUOTES指将单双引号实体化(SQL注入时不能使用单引号闭合)

[![](./img/203765/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01b37a49e15e2676f2.png)

## 审计过程

### <a class="reference-link" name="%E4%B8%80%E3%80%81%E7%AC%AC%E4%B8%80%E5%A4%84%E5%90%8E%E5%8F%B0SQL%E6%B3%A8%E5%85%A5"></a>一、第一处后台SQL注入

用seay的自动审计功能，发现几个点SQL语句时没有用单双引号闭合

[![](./img/203765/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01189134a7721d9817.png)

定位函数，发现需要前置条件，才能执行select语句

[![](./img/203765/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t013012ea3dd5f44696.png)

全局搜索$type变量，发现$type也是可以通过传参控制

[![](./img/203765/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t016c814dd197361931.png)

先尝试对这个文件进行访问<br>
192.168.2.128/xRl4zD_Admin/SEMCMS_Banner.php?type=edit&amp;id=1

[![](./img/203765/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0162b58fe15074b912.png)

需要登录才能执行，使用账号进行登录，再次访问，登录后发现是个banner管理界面

[![](./img/203765/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c302401e5d38111b.png)

去数据库看看sc_banner表里面是什么，以控制ID的值(白盒审计的好处)

[![](./img/203765/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t014115c3aa4b0a6081.png)

给ID传参10后，页面发生了变化，开始尝试SQL注入，由于GET方式请求，过滤了select，union，等于号”=”,可以使用大于号小于号进行测试<br>
192.168.2.128/xRl4zD_Admin/SEMCMS_Banner.php?type=edit&amp;ID=10 or 2&gt;1

[![](./img/203765/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01f76d7be739929c56.png)

感觉可行，由于无法使用联合查询，直接使用盲注查询数据库名<br>
这里使用了三个mysql中的函数，<br>
database()查询当前使用的数据库名<br>
substr(string,start,length);<br>
string为字符串；<br>
start为起始位置；<br>
length为长度。<br>
ascii()返回字符串的ASCII码值<br>
192.168.2.128/xRl4zD_Admin/SEMCMS_Banner.php?type=edit&amp;ID=10 and ascii(substr((database()),1,1))&gt;108

[![](./img/203765/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01839401db077e9494.png)

页面无变化，说明当前数据库名第一个字符的ASCII码值大于108<br>
192.168.2.128/xRl4zD_Admin/SEMCMS_Banner.php?type=edit&amp;ID=10 and ascii(substr((database()),1,1))&gt;110

[![](./img/203765/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01fd283f2c23f4941b.png)

页面出现明显变化，说明当前数据库名第一个字符的ASCII码值小于110<br>
由此可以判断数据库第一个字符的ASCII值等于109<br>
查看ASCII码表可以知道m的ASCII码值为109

[![](./img/203765/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01d93cc16b380a72fb.png)

这里偷了下懒，因为是白盒审计，知道数据库名是mycms，所以直接用m的ascii值去尝试，到这里基本确定存在SQL注入

### <a class="reference-link" name="%E4%BA%8C%E3%80%81%E7%AC%AC%E4%BA%8C%E5%A4%84%E5%90%8E%E5%8F%B0SQL%E6%B3%A8%E5%85%A5"></a>二、第二处后台SQL注入

第二处SQL注入在SEMCMS_Function.php的第81行到92行，我们看到了这个地方有三个自定义函数

[![](./img/203765/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01cbc68fb3ea46d5db.png)

看看这个自定义函数是做什么的。<br>
先看第一个函数：checkdatas

[![](./img/203765/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01d7f90590ea93c4c6.png)

这段代码作用是将变量$str放进sql语句中并执行，返回查询出来的数量，如果查询出来的记录条数大于0，返回1，如果没有记录，则返回0。由于调用这个函数的位置在if语句中，且条件等于0才能继续执行后面的语句，就不能让sql语句查询出记录<br>`if ($Ant-&gt;checkdatas($table,”category_name”,$category_name,$db_conn)==”0″){`<br>
先看看变量$table是什么，$table在第34行被定义

[![](./img/203765/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t018b4326b2b9827d8c.png)

从上面的sql语句中，可以知道$table是一个表的名字。所以这里的sc_categories是一个表，看看这个表里面有什么

[![](./img/203765/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01268b005b2da0366f.png)

我们的目的是不能让sql语句从sc_categories表里面查出数据<br>
看看第二个变量$category_name

[![](./img/203765/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t014b245149a2f1daa9.png)

可以看出这个是一个可以通过POST传参控制的值，猜想这里可不可能存在sql注入，发现sql语句中用了带引号闭合，且在POST传参数调用了test_input函数，所以这里这里可以跳过，现在目的是让他继续执行后面的语句，所以不能让这个sql语句查询出来数据，所以只需要给 $category_name通过POST传一个 sc_categories表中 category_name字段中不存在的数据，这里拿小本本记一下， POST传参category_name且数据库中没有的数据<br>
继续往下看第二个函数

[![](./img/203765/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01abcff24a1d667f11.png)

这个函数的作用是讲数组$val键值分离并在值的两边加上单引号，并写进数据库<br>
哦豁，单引号，好吧，继续，看看参数怎么传的，首先看$val

[![](./img/203765/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t018c2d14a00a8fd852.png)

创建一个名为$val的数组看到有个熟悉的变量$category_name，也就是我们上面的传参会被写入数据库，OK继续看看下一个函数

[![](./img/203765/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01eb0f62187842301c.png)

首先看两个sql语句，第一条$str没有单引号闭合，第二条有单引号闭合，所以要尽量然代码执行第一条，看到前面给$fl的参数，固定为f，很nice。看看变量$str，是由$PID传过来的，我们看看$PID是怎么获取数据的

[![](./img/203765/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01a92d3b79d82ca022.png)

可以看到，PID是通过POST传参，仅通过test_input函数过滤，并没有调用verify_strin()函数。 test_input函数对我们唯一有威胁的就是单双引号被htmlspecialchars($data,ENT_QUOTES)这个函数给html实体化了，但是这里sql语句并没有用单引号闭合！我可以！而且没有经过 verify_strin() 函数过滤，我们穿的之前不能用的union,select,等于号都可以用了<br>
这里记一下， PID可以通过POST传参控制，并且这里有可能是注入点<br>
看看要执行这里的代码需要什么前置条件

[![](./img/203765/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01572d078801ff29c1.png)

首先需要变量$Class等于add，看看$Class能不能控制呢<br>`if (isset($_GET["Class"])){$Class = $_GET["Class"];}else{$Class="";}`<br>
$Class可以通过GET传参控制，也就是需要传参Class=add<br>
继续往上看，还需要什么条件才能进入注入点

[![](./img/203765/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0134baab05b303275a.png)

OK，$CF也是可以控制的，至此条件应该全部满足，在代码上从上往下总结一下需要哪些条件<br>
1、GET传参CF=catagory<br>
2、GET传参Class=add<br>
3、POST传参 category_name 不能等于数据表sc_categories中的category_name字段的值<br>
4、POST传参 PID = PAYLOAD<br>
开始构建数据包，由于POST传参，用上hackerbar，并打开seay的数据库监控插件

[![](./img/203765/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01f1472bcda75c132f.png)

执行后发现类 AntDateProcess 没有找到，类 AntDateProcess 在Include/contorl.php文件中，找找看有没有文件同时包含了这两个文件

[![](./img/203765/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01b785ed002e18be1e.png)

发现好像只有这个A_Admin/SEMCMS_Top_include.php文件包含了，去看看

[![](./img/203765/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0111bf9bda0f838e32.png)

可以看到，这个 A_Admin/SEMCMS_Top_include.php 下还包含了./Include/inc.php，在看看这个./Include/inc.php，下面正好有我需要的 Include/contorl.php ，

[![](./img/203765/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0106b1ddb95554a0ed.png)

这样直接给SEMCMS_Top_include.php传参就行了

[![](./img/203765/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t019da24a1f069f48d5.png)

成功执行sleep(5)语句。<br>
Payload：PID=1 and if(ascii(substr((select table_name from information_schema.tables where table_schema=(database()) limit 0,1),1,1))=115,sleep(5),1)

[![](./img/203765/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01453939ed2ec91d29.png)

### <a class="reference-link" name="%E4%B8%89%E3%80%81%E7%AC%AC%E4%B8%89%E5%A4%84%E5%89%8D%E5%8F%B0SQL%E6%B3%A8%E5%85%A5"></a>三、第三处前台SQL注入

```
第三次sql注入与之前的触发条件不一样，不是由传参引发的
```

在include中web_inc.php文件的第54到第56行

[![](./img/203765/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0194e043bca2c49595.png)

代码的意思是获取url路径，并使用explode函数将字符串打散为数组，将数组的第一个字符串和第二个字符串传给然后web_language_ml函数，看看这个函数做了什么？

[![](./img/203765/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t012abd960a8a10cb16.png)

可以看到$web_urls会被放入数据库语句执行，由于$web_urls获取没有经过POST,GET,以及过滤函数，所以可以确定必定存在SQL注入。<br>
然后我们发现index.php第一个包含的文件就是这个web_inc.php。<br>
那么我们访问index.php对他进行传参就可以了。

[![](./img/203765/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0194b76d314607392b.png)

[![](./img/203765/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01917ae7c00088b0d5.png)

果然执行了，试试一些特殊符号

[![](./img/203765/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01c181def02db6f44f.png)

很有点可惜的是双引号，大于号小于号因为GET传参会自动URL编码，在这个地方获取的时候，也只能获取到编码后的数据。在传进数据库时，url编码被当做字符串处理了，很庆幸单引号没有被解析为字符串，可以完成闭合，试试万能的sleep()吧

[![](./img/203765/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t018b77190ef9f80a81.png)

就连空格都被url编码传进去了， 如果通过burp直接传空格的话空格之后的东西会被直接”吃掉”，用/***/去代替空格也不行，/**之后的也会被吃掉，%0a%0b之类的都不行，会被当成字符串处理，最后用了加号，成功执行的sleep()

[![](./img/203765/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f267dacc883a365b.png)

继续执行下一步，尝试获取数据，先直接在数据库中试试要执行的语句，执行成功后再开始构建payload

[![](./img/203765/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01bd1830e31fd8072b.png)

将空格替换成加号

[![](./img/203765/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01a3981d75369871dd.png)

一个一个加号排除后发现，在”from”、表名、limit两边不能出现加号

[![](./img/203765/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01c7f161a5e393de23.png)

可以用圆括号把表名和字段名括上代替加号，这样表名和”from”两边就不会有加号了

[![](./img/203765/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0199cfe571c851ba35.png)

可行，但是limit两边的加号就没法解决了，那就不用limit吧，取巧用count(),返回查询到的条数

[![](./img/203765/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t019ad1ecf944fc6bb3.png)

payload：192.168.2.128/index.php/1’or+if((select+count(table_name)from(information_schema.tables)where+table_schema=(database()))=15,sleep(5),1)#

[![](./img/203765/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t019218a17bd8060998.png)

有的朋友可能要好奇了，这里只能取出返回条数有什么用？我们是要获取数据。<br>
那么我们不妨试一下我修改后的这条语句。<br>
Payload:<br>[http://192.168.2.128/index.php/1’or+if(substr((select+min(table_name)from(information_schema.tables)where+table_schema=(database())&amp;&amp;table_name!=’sc_banner’),1,1)&gt;’a’,sleep(15),1)#](http://192.168.2.128/index.php/1%E2%80%99or+if(substr((select+min(table_name)from(information_schema.tables)where+table_schema=(database())&amp;&amp;table_name!='sc_banner'),1,1)&gt;'a',sleep(15),1)#)

[![](./img/203765/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0140ecddf0f730f050.png)

延时了15秒<br>
很明显，我们可以通过这样的方法来获取数据库里面的信息。这里存在严重的前台SQL注入。

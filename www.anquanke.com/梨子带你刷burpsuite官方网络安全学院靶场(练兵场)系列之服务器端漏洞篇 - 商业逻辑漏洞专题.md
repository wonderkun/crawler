> 原文链接: https://www.anquanke.com//post/id/245536 


# 梨子带你刷burpsuite官方网络安全学院靶场(练兵场)系列之服务器端漏洞篇 - 商业逻辑漏洞专题


                                阅读量   
                                **49248**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">4</a>
                                </b>
                                                                                    



[![](https://p4.ssl.qhimg.com/t01f90ce5977e44ab1e.png)](https://p4.ssl.qhimg.com/t01f90ce5977e44ab1e.png)



## 本系列介绍

> PortSwigger是信息安全从业者必备工具burpsuite的发行商，作为网络空间安全的领导者，他们为信息安全初学者提供了一个在线的网络安全学院(也称练兵场)，在讲解相关漏洞的同时还配套了相关的在线靶场供初学者练习，本系列旨在以梨子这个初学者视角出发对学习该学院内容及靶场练习进行全程记录并为其他初学者提供学习参考，希望能对初学者们有所帮助。



## 梨子有话说

> 梨子也算是Web安全初学者，所以本系列文章中难免出现各种各样的低级错误，还请各位见谅，梨子创作本系列文章的初衷是觉得现在大部分的材料对漏洞原理的讲解都是模棱两可的，很多初学者看了很久依然是一知半解的，故希望本系列能够帮助初学者快速地掌握漏洞原理。



## 服务器端漏洞篇介绍

> burp官方说他们建议初学者先看服务器漏洞篇，因为初学者只需要了解服务器端发生了什么就可以了



## 服务器端漏洞篇 – 商业逻辑漏洞专题

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AF%E5%95%86%E4%B8%9A%E9%80%BB%E8%BE%91%E6%BC%8F%E6%B4%9E%EF%BC%9F"></a>什么是商业逻辑漏洞？

商业逻辑漏洞，其实很好理解，梨子觉得burp的描述有点过于正经了，感觉有点咬文嚼字的意思，所以梨子就用自己的理解来讲一下什么是商业逻辑漏洞，应用程序的架构和代码都是由不同的工程师来负责的，由于出现了技术或者架构思维上的缺陷，应用程序在执行某个逻辑的时候会很容易被攻击者发现漏洞而进入了奇怪的逻辑，比如我们在讲身份验证专题的时候，我们可以利用代码逻辑上的漏洞绕过验证码阶段直接进入已经处于登录状态的用户，这就是一个简单的逻辑漏洞，还有影响更严重的，比如一些购物平台仅仅通过做加法来计算购物车金额，如果这时候把商品的价格修改成负数的就会导致不仅没有付钱反而还成功购买了商品，当然了，这种漏洞肯定早就修复了，不然现在这些购物平台遇上职业薅羊毛党，那还得了？接下来我们详细地讲解商业逻辑漏洞

### <a class="reference-link" name="%E5%95%86%E4%B8%9A%E9%80%BB%E8%BE%91%E6%BC%8F%E6%B4%9E%E6%98%AF%E6%80%8E%E4%B9%88%E4%BA%A7%E7%94%9F%E7%9A%84%EF%BC%9F"></a>商业逻辑漏洞是怎么产生的？

一般逻辑漏洞是由于开发团队对用户输入的预判不够完全，导致出现了各种意外，这时候就给了攻击者可乘之机，攻击者可以通过修改请求包触发某种意外导致一些意想不到的效果，尤其是越复杂的应用程序逻辑漏洞就越隐蔽，并且危害越大，这就需要架构和开发工程师对整个应用程序了如指掌，以免在架构逻辑或代码逻辑上有任何疏漏

### <a class="reference-link" name="%E5%95%86%E4%B8%9A%E9%80%BB%E8%BE%91%E6%BC%8F%E6%B4%9E%E7%9A%84%E4%BE%8B%E5%AD%90"></a>商业逻辑漏洞的例子

### <a class="reference-link" name="%E5%AF%B9%E5%AE%A2%E6%88%B7%E7%AB%AF%E6%8E%A7%E4%BB%B6%E7%9A%84%E8%BF%87%E5%BA%A6%E4%BF%A1%E4%BB%BB"></a>对客户端控件的过度信任

有的应用程序仅通过前端代码对用户输入进行检测，这就导致攻击者完全可以先利用合规的数据通过前端的检测以后利用burp再修改输入的内容，这样的话风险就非常大了，这种检测根本形同虚设，所以最好是在后端检测，这样不管你怎么改，到了我后台就是你提交的最后版本了，下面我们来看一个例子

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%AF%B9%E5%AE%A2%E6%88%B7%E7%AB%AF%E6%8E%A7%E4%BB%B6%E7%9A%84%E8%BF%87%E5%BA%A6%E4%BF%A1%E4%BB%BB"></a>配套靶场：对客户端控件的过度信任

题目要求我们购买那个什么夹克，但是我们没有那么多钱，我们用burp抓一下包，发现了参数price，我们将其改成一块钱

[![](https://p5.ssl.qhimg.com/t01310c06627c4dfb3a.png)](https://p5.ssl.qhimg.com/t01310c06627c4dfb3a.png)

然后放包，发现我们成功用一块钱就买了一件我们掏空钱包里的钱都买不起的夹克！

### <a class="reference-link" name="%E6%97%A0%E6%B3%95%E5%A4%84%E7%90%86%E9%9D%9E%E5%B8%B8%E8%A7%84%E8%BE%93%E5%85%A5"></a>无法处理非常规输入

企业逻辑的作用是限制用户的输入在允许的范围内，但是毕竟所有的逻辑规则都需要开发团队提前预见用户的输入才能对症下药，肯定会存在开发团队没有预见的情况，这就又给了攻击者可乘之机，让不允许的输入也通过了提前设置的逻辑规则进入后端造成一些意想不到的意外，下面我们来看一段代码

```
$transferAmount = $_POST['amount'];
$currentBalance = $user-&gt;getBalance();

if ($transferAmount &lt;= $currentBalance) `{`
    // Complete the transfer
`}` else `{`
    // Block the transfer: insufficient funds
`}`
```

上面代码是一段用来判断是否有足够余额来转账的逻辑规则，但是逻辑仅判断转账金额是否小于余额，但是并没有判断转正金额是否为正值，那么我们如果修改成负值会发生什么呢，对，会将功能从转账变成充值，余额没有因为转账而减少反而增加了，哇，这就说明逻辑漏洞是非常危险的，会为企业带来巨额的经济和名誉的损失，下面我们通过几个例子来深入讲解

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E9%AB%98%E7%BA%A7%E5%88%AB%E9%80%BB%E8%BE%91%E6%BC%8F%E6%B4%9E"></a>配套靶场：高级别逻辑漏洞

像往常一样，我们拦截结算的包，发现只有一个参数可能存在逻辑漏洞，quantity

[![](https://p2.ssl.qhimg.com/t01e8bf758414c38d37.png)](https://p2.ssl.qhimg.com/t01e8bf758414c38d37.png)

我们还是要买那件夹克，既然我们能修改数量的话，我们就想想改成负数会怎样呢

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01a58d9f56ec1b25ae.png)

我们看到结算的时候真的就因为数量是负的而正负相抵，最后我们成功以极低的价格买到了夹克！

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E4%BD%8E%E7%BA%A7%E5%88%AB%E9%80%BB%E8%BE%91%E7%BC%BA%E9%99%B7"></a>配套靶场：低级别逻辑缺陷

我们像上一题一样修改数量为负数发现已经不生效了，然后我们就尝试将数量调到最大，再利用Intruder的null payload模式无限发包，发现金额到了最大值以后会从负数最小值继续往大增加，就这样继续无限发包，直到我们看到购物车的结算金额到了我们能支付得起的时候停止发包，然后我们就再一次，而且买到了三万多件夹克！

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%BC%82%E5%B8%B8%E5%A4%84%E7%90%86%E4%B8%8D%E4%B8%80%E8%87%B4%E7%9A%84%E8%BE%93%E5%85%A5"></a>配套靶场：异常处理不一致的输入

本来梨子想注册一个administrator，但是提示用户已存在，但是没有忘记密码功能，所以这个思路不太行，既然是要访问管理员面板，那我们试一下/admin这个页面存不存在

[![](https://p3.ssl.qhimg.com/t0185f8313adaba3f10.png)](https://p3.ssl.qhimg.com/t0185f8313adaba3f10.png)

页面存在，但是响应说只有DontWannaCry用户才有访问权限，我们先注册一个普通用户，然后故意让邮箱地址超出最大长度

[![](https://p0.ssl.qhimg.com/t0140a72a2f0fbce95a.png)](https://p0.ssl.qhimg.com/t0140a72a2f0fbce95a.png)

我们发现超出长度的会被截断，所以我们可以构造这样的诡异的邮箱地址来不仅能接收到注册链接又能让注册用户的邮箱是在指定的域(dontwannacry.com)的

[![](https://p2.ssl.qhimg.com/t017bf6537403f8571f.png)](https://p2.ssl.qhimg.com/t017bf6537403f8571f.png)

这样我们就成功注册到了可以进入/admin页面的DontWannaCry用户

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0177518ebecd045304.png)

既然进入了/admin页面，我们就可以删除指定用户了

### <a class="reference-link" name="%E5%AF%B9%E7%94%A8%E6%88%B7%E8%A1%8C%E4%B8%BA%E5%81%9A%E5%87%BA%E9%94%99%E8%AF%AF%E7%9A%84%E9%A2%84%E5%88%A4"></a>对用户行为做出错误的预判

导致这一类逻辑漏洞的原因就是开发团队过于相信用户，对用户的行为做出了错误的预判，比如违反常理的数值的情况就没有做出相应的处理方案，下面我们深入讲解一些典型的情况

### <a class="reference-link" name="%E5%8F%97%E4%BF%A1%E4%BB%BB%E7%9A%84%E7%94%A8%E6%88%B7%E4%B8%8D%E4%BC%9A%E6%B0%B8%E8%BF%9C%E5%8F%AF%E4%BF%A1"></a>受信任的用户不会永远可信

有的应用程序虽然设置了很多逻辑规则来规范用户的输入，但是毕竟人无完人，就总会有遗漏的点，但是应用系统往往会对通过逻辑规则的输入保持完全的信任，这就导致一些虽然通过了逻辑规则但是仍然会对应用程序造成不同程度破坏的输入进入应用程序

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%89%8D%E5%90%8E%E4%B8%8D%E4%B8%80%E7%9A%84%E5%AE%89%E5%85%A8%E6%8E%A7%E5%88%B6"></a>配套靶场：前后不一的安全控制

首先我们进入注册页面

[![](https://p0.ssl.qhimg.com/t012b7e75be88990ca5.png)](https://p0.ssl.qhimg.com/t012b7e75be88990ca5.png)

我们看到有一条提示说公司员工要用公司邮箱注册，这里注册的邮箱填写burp给的临时邮箱，然后用发到这个邮箱的注册链接成功注册，然后登录，我们尝试访问一下/admin页面，但是说得是公司员工才能进，于是我们就尝试修改当前用户的邮箱，反正都注册成功了

[![](https://p3.ssl.qhimg.com/t017d760a7d6e3c1b00.png)](https://p3.ssl.qhimg.com/t017d760a7d6e3c1b00.png)

发现我们可以不需要任何验证就进行修改，然后我们就可以访问/admin页面了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t019aad8d165f8968a3.png)

然后我们就可以删除指定用户了

### <a class="reference-link" name="%E7%94%A8%E6%88%B7%E4%B8%8D%E5%8F%AF%E8%83%BD%E6%80%BB%E6%98%AF%E5%A1%AB%E5%86%99%E5%BF%85%E5%A1%AB%E9%A1%B9"></a>用户不可能总是填写必填项

啊，burp讲话好啰嗦啊，一两句就能讲明白的东西居然讲那么一大段话，所以说，梨子这个系列是帮助大家理解非常好的系列哦，有的时候用户在填写表单的时候都会有一些必填项，但是有的应用程序仅在前端对表单的必填项是否有值做校验，这就导致攻击者完全可以通过拦截请求包的方式清空必填项的值，因为是非常规的表单，就肯定也会导致一些意想不到的情况，为了能够全面地进行测试，可以一次只清空一个必填字段甚至把该参数都删掉，观察不同情况下的差异

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%A4%9A%E7%94%A8%E9%80%94%E7%9A%84%E7%AB%AF%E7%82%B9%E4%B9%8B%E9%97%B4%E7%9A%84%E5%BC%B1%E9%9A%94%E7%A6%BB"></a>配套靶场：多用途的端点之间的弱隔离

我们登录测试用户，然后进入修改密码页面，拦截请求包，然后将用户名修改成administrator，并且删除原密码字段

[![](https://p5.ssl.qhimg.com/t012b7ff77b35fd0413.png)](https://p5.ssl.qhimg.com/t012b7ff77b35fd0413.png)

放包，发现可以不需要旧密码就能修改administrator的密码，我们就可以用新密码登录并且删除指定用户了

### <a class="reference-link" name="%E7%94%A8%E6%88%B7%E4%B8%8D%E5%8F%AF%E8%83%BD%E6%80%BB%E6%98%AF%E5%BE%AA%E8%A7%84%E8%B9%88%E7%9F%A9"></a>用户不可能总是循规蹈矩

这个就很好理解了，因为我们在身份验证专题讲过一种情况，用户在输入用户名密码以后账户其实已经处于登录状态了，这时候直接将URL改成用户主页就可以跳过验证码阶段，这就是不循规蹈矩的结果，不仅可以跳过某些步骤，还可以通过重放包的方式打乱请求的执行序列，也是可以导致一些意想不到的效果的，总之就是用非常人的思路就可能挖掘到逻辑漏洞

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%B7%A5%E4%BD%9C%E6%B5%81%E7%A8%8B%E9%AA%8C%E8%AF%81%E4%B8%8D%E8%B6%B3"></a>配套靶场：工作流程验证不足

我们先随便购买一个便宜的商品，发现比买不起的情况多出一个请求

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01f28d433c82443286.png)

所以我们猜测重放这个请求包就会直接将购物车的所有东西付款，于是我们添加那个夹克到购物车，然后重放那个包，发现成功购买到我们梦寐以求的夹克！

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%88%A9%E7%94%A8%E6%9C%89%E7%BC%BA%E9%99%B7%E7%9A%84%E7%8A%B6%E6%80%81%E6%9C%BA%E8%BF%9B%E8%A1%8C%E8%BA%AB%E4%BB%BD%E9%AA%8C%E8%AF%81%E7%BB%95%E8%BF%87"></a>配套靶场：利用有缺陷的状态机进行身份验证绕过

首先我们登录，然后拦截下一个包，就是选择角色的，丢掉这个包，然后我们发现我们进去以后就是administrator身份了

然后我们就可以删除指定用户了

### <a class="reference-link" name="%E7%89%B9%E5%AE%9A%E9%A2%86%E5%9F%9F%E7%9A%84%E7%BC%BA%E9%99%B7"></a>特定领域的缺陷

有一些逻辑漏洞是发生在某些特定领域的，比如商城的打折功能，如果要找关于这一类的逻辑漏洞就需要知道打折的作用，作用肯定就是能打折购买嘛，但是如果应用程序仅在前端验证折扣力度，并没有办法在后端验证折扣力度是否在允许范围内，这就可能导致攻击者可以通过拦截请求包并修改表示折扣力度的参数值来以超低价甚至免费的价格成功购买某个产品，所以在寻找这类漏洞的时候需要稍微了解一下那个领域的一些专业知识，越复杂的领域需要了解的越多，也可以换一种说法就是要摸清应用程序所属的业务才能去寻找相关的逻辑漏洞

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%95%86%E4%B8%9A%E8%A7%84%E5%88%99%E7%9A%84%E5%BC%BA%E5%88%B6%E6%89%A7%E8%A1%8C%E7%BC%BA%E9%99%B7"></a>配套靶场：商业规则的强制执行缺陷

我们登录以后发现给了我们一个优惠码，然后我们再来到首页有个sign up，注册以后发现会再给我们一个优惠码，于是我们试试这两个优惠码可不可以叠加，不行，那交替使用呢，发现可以，于是我们不断操作几次直到支付金额归零，成功购买到梦寐以求的夹克！

[![](https://p3.ssl.qhimg.com/t0182162714bd91187c.png)](https://p3.ssl.qhimg.com/t0182162714bd91187c.png)

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E6%97%A0%E9%99%90%E9%87%91%E9%92%B1%E9%80%BB%E8%BE%91%E7%BC%BA%E9%99%B7"></a>配套靶场：无限金钱逻辑缺陷

和上一题一样，只不过我们这次只有一个优惠码， 是一个打七折的优惠码，买任何东西都可以打七折，那么我们想要买夹克只需要935.9，所以我们需要想办法凑够这个金额，然后我们发现礼品卡原价10，用优惠码买只需要7，但是会增加余额10，这就相当于赚了3，于是我们利用之前学习过的宏技术设置如下顺序的请求包序列

[![](https://p3.ssl.qhimg.com/t01c7b2ebf49ef652b2.png)](https://p3.ssl.qhimg.com/t01c7b2ebf49ef652b2.png)

梨子来简单解释一下这个请求包序列，先是把礼品卡加购物车，然后使用优惠码，确认订单，结算，兑换礼品卡，这里有一个和之前不太一样的知识点，我们看到在结算以后会在响应中找到一个礼品卡的兑换码，如果我们想要请求包序列自动顺序执行的话，我们需要把兑换码从第4个请求包中提取出来然后传给第5个请求包，我们选中第4个请求包，点击”configure items”，并提取兑换码存到我们的自定义参数中

[![](https://p3.ssl.qhimg.com/t018c1f80985202f62f.png)](https://p3.ssl.qhimg.com/t018c1f80985202f62f.png)

[![](https://p0.ssl.qhimg.com/t01fc6ec7bbf8f3fc1e.png)](https://p0.ssl.qhimg.com/t01fc6ec7bbf8f3fc1e.png)

[![](https://p4.ssl.qhimg.com/t01720eec52d73fd2e5.png)](https://p4.ssl.qhimg.com/t01720eec52d73fd2e5.png)

然后我们再选中第5个请求包，点击”configure items”，然后将获取Gift-Card参数的方式修改成如下方式

[![](https://p4.ssl.qhimg.com/t01b7b063796b8b6d63.png)](https://p4.ssl.qhimg.com/t01b7b063796b8b6d63.png)

为了验证我们设置的有没有问题，我们可以”test macro”观察一下，如果出现bug可能是burp版本有问题，可以升级一下哦，然后我们需要不断重放这个请求序列，为了能够直观地看到我们的余额是否满足要求，我们将用户中心请求发到Intruder，然后利用快速选取正则匹配自动提取余额字段，开始不断重放

[![](https://p5.ssl.qhimg.com/t011871baffb4065f4a.png)](https://p5.ssl.qhimg.com/t011871baffb4065f4a.png)

等待一段时间后，余额终于满足要求了，终于可以买到梦寐以求的夹克了！

[![](https://p5.ssl.qhimg.com/t01558265be95a56ac8.png)](https://p5.ssl.qhimg.com/t01558265be95a56ac8.png)

### <a class="reference-link" name="%E6%8F%90%E4%BE%9B%E4%B8%80%E4%B8%AA%E5%8A%A0%E8%A7%A3%E5%AF%86%E6%8E%A5%E5%8F%A3"></a>提供一个加解密接口

有的应用程序虽然使用了加密功能，但是因为应用程序在进行加密解密的时候每次都使用的是相同的密钥，导致我们不需要知道应用程序使用的是何种加密方式及密钥即可通过加密点解密点构造我们想要的密文，这么讲好像不太能理解，下面我们通过一个配套靶场来深入讲解

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%88%A9%E7%94%A8%E5%8A%A0%E8%A7%A3%E5%AF%86%E6%8E%A5%E5%8F%A3%E7%BB%95%E8%BF%87%E8%BA%AB%E4%BB%BD%E9%AA%8C%E8%AF%81"></a>配套靶场：利用加解密接口绕过身份验证

我们登录进来以后发现用户中心只有一个修改邮箱地址的功能点，于是我们随便输入点东西看一下会有什么反馈

[![](https://p0.ssl.qhimg.com/t01f238ab4fa4c03c8e.png)](https://p0.ssl.qhimg.com/t01f238ab4fa4c03c8e.png)

我们发现如果邮箱地址格式不合规的话会在页面中回显这么一句话，我们看一下请求包是什么样的

[![](https://p0.ssl.qhimg.com/t01d1b195838c1e5681.png)](https://p0.ssl.qhimg.com/t01d1b195838c1e5681.png)

我们在提交修改邮箱地址请求以后，提示语句会被加密并存入Cookie字段的notification参数中，我们再来追踪一下重定向

[![](https://p1.ssl.qhimg.com/t01ba290bf025309623.png)](https://p1.ssl.qhimg.com/t01ba290bf025309623.png)

好的，我们看到Cookie字段的notification参数值会被解密并回显到响应中，于是我们相当于找到了一个加密点一个解密点，然后我们看到Cookie字段的stay-logged-in参数值与这个也有点类似，于是我们将其替换过去再看一下

[![](https://p1.ssl.qhimg.com/t01d1b98e399eb7fc6b.png)](https://p1.ssl.qhimg.com/t01d1b98e399eb7fc6b.png)

我们惊奇地发现是可以成功在解密点解出的，说明解密点是通用的，那么加密点就也是通用的，然后通过观察发现stay-logged-in的明文形式是由用户名与时间戳以冒号分隔开的格式构成的，于是我们将wiener换成administrator以后加密，并尝试解密

[![](https://p4.ssl.qhimg.com/t01f685c6b766665a7f.png)](https://p4.ssl.qhimg.com/t01f685c6b766665a7f.png)

我们看到是可以成功构造的，但是stay-logged-in明文形式不应该包含前面那一串”Invalid email address: “，所以我们要想办法把它去掉，然后因为这个是对称加密，就是原文有多长，密文就会有多长，所以我们尝试直接删除明文中相应数量的字节，将密文发到decoder，在十六进制下删除23字节(因为那串无用前缀有23字节长)

[![](https://p1.ssl.qhimg.com/t01c2a80a9c3980f423.png)](https://p1.ssl.qhimg.com/t01c2a80a9c3980f423.png)

[![](https://p3.ssl.qhimg.com/t01cedaa9b84e0845a8.png)](https://p3.ssl.qhimg.com/t01cedaa9b84e0845a8.png)

删除以后再按照原格式编码回去，在解密点看看能不能解密出来

[![](https://p0.ssl.qhimg.com/t011bbdfa29246f8d04.png)](https://p0.ssl.qhimg.com/t011bbdfa29246f8d04.png)

发现会有报错，说密码密文分块必须是16的倍数，于是我们需要填充一些字节让其达到16的倍数，所以我们填充9个无用字符，然后因为是无用的，填充完以后再删除32字节就可以正常解密了

[![](https://p0.ssl.qhimg.com/t012a9091cc33ac005c.png)](https://p0.ssl.qhimg.com/t012a9091cc33ac005c.png)

我们就成功地构造出不仅没有无用前缀而且还能成功解密的密文，于是我们将其替换到stay-logged-in参数值，并替换成新的session值，发现我们就可以进入administrator用户页面了

[![](https://p5.ssl.qhimg.com/t01f791cb85767d23bf.png)](https://p5.ssl.qhimg.com/t01f791cb85767d23bf.png)

然后我们就能删除指定用户了

[![](https://p0.ssl.qhimg.com/t01d50423d5dd0f8459.png)](https://p0.ssl.qhimg.com/t01d50423d5dd0f8459.png)



## 如何防止商业逻辑漏洞？

burp总结了两点防止此类漏洞的方法
- 确保开发和测试人员了解应用程序所属的领域
- 避免对用户行为或应用程序其他部分的行为做出默认信任
言外之意就是不要太相信用户输入，尽量做到严格的过滤，把能想到的情况都考虑到，所以需要开发和测试人员对业务非常地熟悉才能预想出大部分可能发生的情况，这里burp给出了一个实践指南
- 维护所有事务和工作流的清晰的设计文档和数据流，并注意在每个阶段所做的任何假设
- 尽可能清晰地编写代码
- 注意对使用每个组件的其他代码的任何引用


## 总结

以上就是梨子带你刷burpsuite官方网络安全学院靶场(练兵场)系列之服务器端漏洞篇 – 商业逻辑漏洞专题的全部内容了，本专题呢主要介绍了逻辑漏洞的常见情况，主要就是因为开发和测试人员对业务不够熟悉，未能对所有可能发生的情况做出相应的处置方案并且默认完全信任通过逻辑规则的用户输入，所以说逻辑漏洞还是很危险的，尤其是越复杂的业务系统，逻辑漏洞的发现难度越大，其危害就越大，还是不容忽视的，大家如果有什么疑问可以在评论区讨论哦！

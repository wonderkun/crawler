> 原文链接: https://www.anquanke.com//post/id/84805 


# 【技术分享】开源SRC项目、团队内部贡献平台Mooder


                                阅读量   
                                **146940**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



**[![](https://p3.ssl.qhimg.com/t0132f44711bda16c52.jpg)](https://p3.ssl.qhimg.com/t0132f44711bda16c52.jpg)**

**小介绍**

Mooder是一款开源、安全、简洁、强大的（安全）团队内部知识分享平台，基于Django、全封闭保证私密性、支持Markdown、支持Postgres/Mysql/Sqlite等多种数据库、支持Docker-compose一键化安装与更新，易于二次开发。

今天开源的一个小玩意，上个月到这个月陆陆续续写的，这几天下班以后也会写几行这个，进行产品上的微调，然后修一些BUG。本来是给自己团队写的一个东西，但想想感觉应该有很多团队都需要这个，于是就开源了。

项目地址： [https://github.com/phith0n/mooder](https://github.com/phith0n/mooder)

文档地址： [https://phith0n.github.io/mooder/](https://phith0n.github.io/mooder/)

<br>

**为什么会有Mooder**

有的人把Mooder理解为一个漏洞平台：团队成员可以提交漏洞，管理员进行审核与评分，最后能够兑换礼品或兑换其他人的漏洞。

但我把它理解为一个“团队贡献”平台，绝不是分享漏洞，而是分享知识。最初我在设计Minos的时候就有这样的想法，只可惜后面走偏了，把Minos做成一个社区了。后来我想想，还是需要这么一个东西，于是我又写了Mooder。

一个团队需要有自己独一无二的内容，才能吸引更多人才，而这个平台将是承载这些内容的载体。

做Mooder的初衷是为了团队内部的交流。由于众所周知的原因，国内大量社区关闭，安全技术知识的学习变得愈加困难，更多的团队将交流方式变为QQ群、微信群。 而QQ、微信等及时通信工具并不是一个交流技术的好地方，团队仍然需要一个内部社区。

Mooder从设计之初想法就是“封闭”，也就是说该社区严格控制内部隐私，仅拥有邀请码的用户可以登录社区，管理员在后台也能够踢出、删除一个用户，保证了社区的私密性。

另外，Mooder的核心理念的“贡献知识”。团队成员可以将自己挖掘的通用漏洞、编写的EXP、提交到其他SRC的漏洞详情、众测中挖到的漏洞等等作为一个“贡献”提交到Mooder中，然后由管理员进行审核并给予rank与积分。通过该“积分”，团队成员也可以购买其他成员提交的贡献，或者去礼品中心换取礼品等。

通过这样的“知识交换”，让团队能够更快地成长。

<br>

**一些小预览**

**用户登录**

Mooder支持登录、邀请码注册、找回密码、登录激活。

[![](https://p5.ssl.qhimg.com/t0172607d8f3ff3a196.jpg)](https://p5.ssl.qhimg.com/t0172607d8f3ff3a196.jpg)

注册：<br>

[![](https://p3.ssl.qhimg.com/t0150a81daca7ff7928.jpg)](https://p3.ssl.qhimg.com/t0150a81daca7ff7928.jpg)

**查看贡献**

贡献列表，列出所有贡献：

[![](https://p5.ssl.qhimg.com/t0171f9579491004363.jpg)](https://p5.ssl.qhimg.com/t0171f9579491004363.jpg)

详情页面，根据贡献的私密程度判断用户是否可读。

用户在提交贡献的时候可以选择该贡献的可见性：公开、出售或私密。公开的贡献，所有平台注册用户均可查看；出售的贡献，其他用户需要付出一定价格购买，才能查看当前贡献，而贡献提交者将可以或者这笔费用；私密的贡献，除贡献作者与审核员外任何人无法查看。

[![](https://p5.ssl.qhimg.com/t019c0f89ba0dbd4b9a.jpg)](https://p5.ssl.qhimg.com/t019c0f89ba0dbd4b9a.jpg)

**提交与审核贡献**

提交贡献支持Markdown编辑详情，支持上传图片与附件，支持预览：

[![](https://p2.ssl.qhimg.com/t01d667f3f18ad807ee.jpg)](https://p2.ssl.qhimg.com/t01d667f3f18ad807ee.jpg)

管理员后台审核贡献：

[![](https://p2.ssl.qhimg.com/t01286bcdb89d01b5a7.jpg)](https://p2.ssl.qhimg.com/t01286bcdb89d01b5a7.jpg)

**礼品中心**

团队负责人可以在后台进行礼品上架，用于奖励乐于分享的成员。前台礼品中心：

[![](https://p3.ssl.qhimg.com/t0180e953dc12c8a53b.jpg)](https://p3.ssl.qhimg.com/t0180e953dc12c8a53b.jpg)

用户填写收货地址进行礼品兑换：

[![](https://p5.ssl.qhimg.com/t01c12e726f415ba5d1.jpg)](https://p5.ssl.qhimg.com/t01c12e726f415ba5d1.jpg)

管理员后台查看购买记录：

[![](https://p2.ssl.qhimg.com/t016c705f2c30f9d6b9.jpg)](https://p2.ssl.qhimg.com/t016c705f2c30f9d6b9.jpg)

虚拟物品可以直接通过“管理员回复”发货：

[![](https://p1.ssl.qhimg.com/t011be42575447baa9c.jpg)](https://p1.ssl.qhimg.com/t011be42575447baa9c.jpg)

**后台管理**

审核员后台，可以方便地进行贡献（漏洞）的审核，也能极好的控制权限——可以控制审核员只能审核贡献、运营人员只能修改礼品与发货。

后台首页显示一些统计信息：

[![](https://p1.ssl.qhimg.com/t01ffe0debdee40d2a4.jpg)](https://p1.ssl.qhimg.com/t01ffe0debdee40d2a4.jpg)

一键生成邀请码：

[![](https://p5.ssl.qhimg.com/t01a238ac7070306b01.jpg)](https://p5.ssl.qhimg.com/t01a238ac7070306b01.jpg)

增加内部应用：

[![](https://p5.ssl.qhimg.com/t012669d1f90a78a97c.jpg)](https://p5.ssl.qhimg.com/t012669d1f90a78a97c.jpg)

用户奖惩：

[![](https://p0.ssl.qhimg.com/t0124f0d422005559c1.jpg)](https://p0.ssl.qhimg.com/t0124f0d422005559c1.jpg)



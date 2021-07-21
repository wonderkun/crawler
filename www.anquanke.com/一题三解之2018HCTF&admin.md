> 原文链接: https://www.anquanke.com//post/id/164086 


# 一题三解之2018HCTF&amp;admin


                                阅读量   
                                **403700**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">7</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t014158d921341bc24e.jpg)](https://p1.ssl.qhimg.com/t014158d921341bc24e.jpg)



## 前言

有幸拿到了这道题的1血，也在赛后的交流讨论中，发现了一些新的思路，总结一下3个做法：
- 法1：伪造session
- 法2：unicode欺骗
- 法3：条件竞争


## 信息搜集

拿到题目

f12查看源代码

发现提示要成为admin

随便注册个账号，登入后，在

发现提示

于是下载源码



## 功能分析

拿到代码后，简单的查看了下路由

查看一下路由，功能非常单一：登录，改密码，退出，注册，edit。

但edit功能也是个假功能，并且发现并不会存在sql注入之类的问题，也没有文件写入或者是一些危险的函数，此时陷入了困境。



## 解法一：session伪造

### <a name="%E5%88%9D%E6%AD%A5%E6%8E%A2%E7%B4%A2"></a>初步探索

想到的第一个方法：session伪造

于是尝试伪造session，根据ph写的文章

可以知道flask仅仅对数据进行了签名。众所周知的是，签名的作用是防篡改，而无法防止被读取。而flask并没有提供加密操作，所以其session的全部内容都是可以在客户端读取的，这就可能造成一些安全问题。

所以我们构造脚本

然后可以尝试读取我们的session内容

[![](https://p5.ssl.qhimg.com/t01d379cb422b901767.png)](https://p5.ssl.qhimg.com/t01d379cb422b901767.png)

此时容易想到伪造admin得到flag，因为看到代码中

[![](https://p2.ssl.qhimg.com/t017e7e3269015fdfd8.png)](https://p2.ssl.qhimg.com/t017e7e3269015fdfd8.png)

想到把name伪造为admin，于是github上找了个脚本

尝试伪造

但是需要SECRET_KEY

我们发现config.py中存在

于是尝试ckj123

[![](https://p3.ssl.qhimg.com/t011f2f495345b7b523.png)](https://p3.ssl.qhimg.com/t011f2f495345b7b523.png)

但是比赛的时候很遗憾，最后以失败告终，当时以为key不是SECRET_KEY，就没有深究

后来发现问题https://graneed.hatenablog.com/entry/2018/11/11/212048

似乎python3和python2的flask session生成机制不同

[![](https://p5.ssl.qhimg.com/t01ccc362b56b3fc055.png)](https://p5.ssl.qhimg.com/t01ccc362b56b3fc055.png)

改用python3生成即可成功伪造管理员

[![](https://p1.ssl.qhimg.com/t01312c49a0bdefdff2.png)](https://p1.ssl.qhimg.com/t01312c49a0bdefdff2.png)



## 解法二：Unicode欺骗

### <a name="%E4%BB%A3%E7%A0%81%E5%AE%A1%E8%AE%A1"></a>代码审计

在非常迷茫的时候，肯定想到必须得结合改密码功能，那会不会是change这里有问题，于是仔细去看代码，发现这样一句

[![](https://p1.ssl.qhimg.com/t01a62718e1f4b58647.png)](https://p1.ssl.qhimg.com/t01a62718e1f4b58647.png)

好奇怪，为什么要转小写呢？

难道注册的时候没有转大小写吗？

[![](https://p0.ssl.qhimg.com/t0185c9b99610dec9e3.png)](https://p0.ssl.qhimg.com/t0185c9b99610dec9e3.png)

[![](https://p2.ssl.qhimg.com/t0142ed79c38e510873.png)](https://p2.ssl.qhimg.com/t0142ed79c38e510873.png)

但随后发现注册和登录都用了转小写，注册ADMIN的计划失败

但是又有一个特别的地方，我们python转小写一般用的都是lower()，为什么这里是strlower()?

有没有什么不一样的地方呢？于是想到跟进一下函数

本能的去研究了一下nodeprep.prepare

找到对应的库

这个方法很容易懂，即将大写字母转为小写

但是很快就容易发现问题

[![](https://p2.ssl.qhimg.com/t01c3ca861181957082.png)](https://p2.ssl.qhimg.com/t01c3ca861181957082.png)

[![](https://p5.ssl.qhimg.com/t01ece0c53877fc0052.png)](https://p5.ssl.qhimg.com/t01ece0c53877fc0052.png)

版本差的可真多，十有八九这里有猫腻

### <a name="unicode%E9%97%AE%E9%A2%98"></a>unicode问题

后来搜到这样一篇文章

对于如下字母

[![](https://p1.ssl.qhimg.com/t01b1cdb8fd0fdb6a3c.png)](https://p1.ssl.qhimg.com/t01b1cdb8fd0fdb6a3c.png)

具体编码可查https://unicode-table.com/en/search/?q=small+capital

nodeprep.prepare会进行如下操作

[![](https://p1.ssl.qhimg.com/t01e6150cb114639c0d.png)](https://p1.ssl.qhimg.com/t01e6150cb114639c0d.png)

即第一次将其转换为大写，第二次将其转换为小写

那么是否可以用来bypass题目呢？

### <a name="%E6%94%BB%E5%87%BB%E6%9E%84%E9%80%A0"></a>攻击构造

我们容易想到一个攻击链：
- 注册用户ᴀdmin
- 登录用户ᴀdmin，变成Admin
- 修改密码Admin，更改了admin的密码
于是成功得到如下flag

[![](https://p4.ssl.qhimg.com/t01ff30572eb8252865.png)](https://p4.ssl.qhimg.com/t01ff30572eb8252865.png)

### <a name="%E6%89%A9%E5%B1%95"></a>扩展

这里的unicode欺骗，让我想起了一道sql注入题目



## 解法三：条件竞争

该方法也是赛后交流才发现的，感觉有点意思

### <a name="%E4%BB%A3%E7%A0%81%E5%AE%A1%E8%AE%A1"></a>代码审计

我们发现代码在处理session赋值的时候

[![](https://p2.ssl.qhimg.com/t015483fb615c3f782b.png)](https://p2.ssl.qhimg.com/t015483fb615c3f782b.png)

[![](https://p4.ssl.qhimg.com/t0169918a9c850e8ec9.png)](https://p4.ssl.qhimg.com/t0169918a9c850e8ec9.png)<br>
两个危险操作，一个登陆一个改密码，都是在不安全check身份的情况下，直接先赋值了session

那么这里就会存在一些风险

那么我们设想，能不能利用这一点，改掉admin的密码呢？

例如：
- 我们登录sky用户，得到session a
- 用session a去登录触发admin赋值
- 改密码，此时session a已经被更改为session b了，即session name=admin
- 成功更改admin的密码
但是构想是美好的，这里存在问题，即前两步中，如果我们的Session a是登录后的，那么是无法再去登录admin的

[![](https://p2.ssl.qhimg.com/t019e3bbbe0d730d41d.png)](https://p2.ssl.qhimg.com/t019e3bbbe0d730d41d.png)

我们会在第一步直接跳转，所以这里需要条件竞争

### <a name="%E6%9D%A1%E4%BB%B6%E7%AB%9E%E4%BA%89%E6%80%9D%E8%B7%AF"></a>条件竞争思路

那么能不能避开这个check呢？

答案是显然的，我们双线并进

当我们的一个进程运行到改密码

[![](https://p0.ssl.qhimg.com/t01d48a760805ea0e10.png)](https://p0.ssl.qhimg.com/t01d48a760805ea0e10.png)

这里的时候

我们的另一个进程正好退出了这个用户，并且来到了登录的这个位置

[![](https://p3.ssl.qhimg.com/t018dad3539436692a9.png)](https://p3.ssl.qhimg.com/t018dad3539436692a9.png)

此时正好session name变为admin，change密码正好更改了管理员密码

### <a name="payload"></a>payload

这里直接用研友syang[@Whitzard](https://github.com/Whitzard)的脚本了

注：但在后期测试中我没能成功，后面再研究一下，但我认为思路应该是正确的。



## 后记

题目可能因为一些失误有一些非预期，但是能进行这么多解法，对学习还是非常有帮助的。

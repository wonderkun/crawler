> 原文链接: https://www.anquanke.com//post/id/185252 


# 警惕垃圾邮件 伪造法院传真传播Sodinokibi勒索病毒


                                阅读量   
                                **397062**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p1.ssl.qhimg.com/t017e28de5dc98f1ccc.jpg)](https://p1.ssl.qhimg.com/t017e28de5dc98f1ccc.jpg)



Sodinokibi勒索病毒在国内首次被发现于2019年4月份，2019年5月24日首次在意大利被发现，在意大利被发现使用RDP攻击的方式进行传播感染，这款病毒被称为GandCrab勒索病毒的接班人，在GandCrab勒索病毒运营团队停止更新之后，就马上接管了之前GandCrab的传播渠道，经过近半年的发展，这款勒索病毒使用了多种传播渠道进行传播扩散，如下所示：

Oracle Weblogic Server漏洞<br>
Flash UAF漏洞<br>
RDP攻击<br>
垃圾邮件<br>
水坑攻击<br>
漏洞利用工具包和恶意广告下载

自从GandCrab停止更新之后，这款勒索病毒迅速流行，国内外已经有不少企业中招，微信上一个朋友又发来勒索病毒求助信息，如下所示：

[![](https://p2.ssl.qhimg.com/t01d354573aad40260e.png)](https://p2.ssl.qhimg.com/t01d354573aad40260e.png)

通过了解，这位朋友是打开了一个邮件附件，然后被加密勒索，如下：

[![](https://p2.ssl.qhimg.com/t01dc9fa55c141a699a.png)](https://p2.ssl.qhimg.com/t01dc9fa55c141a699a.png)

勒索病毒提示信息文本文件和样本，如下：

[![](https://p1.ssl.qhimg.com/t01e1c9a489b9f4edb3.png)](https://p1.ssl.qhimg.com/t01e1c9a489b9f4edb3.png)

拿到勒索提示信息和样本，基本可以确认是Sodinokibi勒索病毒了，相关的勒索提示信息，如下所示：

[![](https://p0.ssl.qhimg.com/t01d15dda67c2b93549.png)](https://p0.ssl.qhimg.com/t01d15dda67c2b93549.png)

垃圾邮件信息，如下所示：

[![](https://p1.ssl.qhimg.com/t01d1df399b4d025477.png)](https://p1.ssl.qhimg.com/t01d1df399b4d025477.png)

发件人邮箱地址:[user@qixinge.club](mailto:user@qixinge.club)，伪造中华人民共和国最高人民法院的传真，给受害者发送垃圾邮件，然后附加上勒索病毒，样本采用了DOC的图片，迷惑受害者，如下所示：

[![](https://p1.ssl.qhimg.com/t01ab7d56b1249221a8.png)](https://p1.ssl.qhimg.com/t01ab7d56b1249221a8.png)

主要是利用一些受害者安全意识比较薄弱的特点，直接打开附件中的程序文档，然后中招，被加密勒索，通过垃圾邮件传播也是一些勒索病毒团伙常用的技巧，主要还是因为很多人对勒索病毒并不了解，然后自身安全意识也不够强，以为不会被勒索……

[![](https://p2.ssl.qhimg.com/t011fa52556f1ab3cd4.png)](https://p2.ssl.qhimg.com/t011fa52556f1ab3cd4.png)

通过分析这款勒索病毒样本，跟之前一样，也采用了混淆加密的外壳，通过动态调试，可以在内存中解密获取到勒索病毒的核心代码，如下所示：

[![](https://p0.ssl.qhimg.com/t01536be7dbd5e4e904.png)](https://p0.ssl.qhimg.com/t01536be7dbd5e4e904.png)

对比之前Sodinokibi勒索病毒代码，如下所示：

[![](https://p5.ssl.qhimg.com/t01d4900d74fba41a8d.png)](https://p5.ssl.qhimg.com/t01d4900d74fba41a8d.png)

代码相应度达到90%以上，确认此勒索病毒为Sodinokibi变种，此勒索病毒加密后的文件，如下所示：

[![](https://p5.ssl.qhimg.com/t01b0affeddbb15ca98.png)](https://p5.ssl.qhimg.com/t01b0affeddbb15ca98.png)

同时会修改桌面背景，如下所示：

[![](https://p0.ssl.qhimg.com/t01f192c70a62c131fc.png)](https://p0.ssl.qhimg.com/t01f192c70a62c131fc.png)

此勒索病毒解密网站，如下所示：

[![](https://p3.ssl.qhimg.com/t01325d8958872d40ca.png)](https://p3.ssl.qhimg.com/t01325d8958872d40ca.png)

勒索金额为0.12805337BTC，超过期限之后为0.25610674BTC，黑客BTC钱包地址：

3J7XVA4BRKSEbsbkn3LZzt8xAnszik8FKH

此前的BTC钱包地址：

3Fxn6x58FvreuBA9ECyxYdx8dQnDuZhxMj<br>
3AXsdbxDtWd8BKw2tfZxH1nb3rXLKFFxXY<br>
3JxrembpZuzsMVxtr7NBy2sxX1MhEiaRnf

黑产团伙利用垃圾邮件传播勒索病毒，主要是利用受害者安全意识不强，当收到垃圾邮件之后，立即打开邮件中的附件程序，勒索病毒运行导致系统被加密勒索，此勒索病毒目前主要通过垃圾邮件，RDP爆破，CVE漏洞等进行传播，目前此勒索病毒暂无法解密，全球也没有哪家安全公司或组织发布相关解密工具，请大家一定要提高自己的安全意识，警惕垃圾邮件，更不要轻易打开邮件中的附件

最近一两年针对企业的勒索病毒攻击越来越多，不断有朋友通过微信联系我，给我反馈各种勒索病毒相关信息，在此感谢各位朋友，大部分勒索病毒还不能解密，希望企业做好相应的勒索病毒防御措施，提高员工的安全意识，不要以为没了中勒索就没事，事实上黑产每天都在不断发起勒索攻击，不要等到中了勒索病毒才知道安全的重要性

本文转自：[安全分析与研究](https://mp.weixin.qq.com/s/GjnsNhMep-gTEjCR0WSNTw)

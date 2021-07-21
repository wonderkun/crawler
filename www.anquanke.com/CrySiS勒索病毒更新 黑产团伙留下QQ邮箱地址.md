> 原文链接: https://www.anquanke.com//post/id/185340 


# CrySiS勒索病毒更新 黑产团伙留下QQ邮箱地址


                                阅读量   
                                **391444**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">4</a>
                                </b>
                                                                                    



[![](https://p0.ssl.qhimg.com/t01602fd17b315a1cf6.jpg)](https://p0.ssl.qhimg.com/t01602fd17b315a1cf6.jpg)



昨天在微信群里有个朋友给我留言，说有一款CrySiS样本使用QQ邮箱做为联系方式，让我看看

[![](https://p5.ssl.qhimg.com/t0180e43dae6d60ac5f.jpg)](https://p5.ssl.qhimg.com/t0180e43dae6d60ac5f.jpg)

事实上CrySiS这款勒索病毒早在二月份就在人在腾讯的一个群里咨询过，同时也想咨询腾讯的相关人员，能不能通过QQ查到一些信息之类的，此前我就怀疑是不是国内的一些黑产团伙通过在线购买CrySiS的RAAS平台上生成的病毒样本，然后在国内进行传播感染，获取暴利？不过这仅仅是猜测，因为没有证据，至今也没有抓到过相关的黑产团伙，通过这些QQ邮箱我也没办法拿到相关信息……

此勒索病毒加密后的文件，如下所示：

[![](https://p4.ssl.qhimg.com/t016922b00156dc2b7b.png)](https://p4.ssl.qhimg.com/t016922b00156dc2b7b.png)

加密后缀名为id-[用户ID号]. [[3442516480@qq.com](mailto:3442516480@qq.com)].pdf，并弹出勒索提示信息，如下所示：

[![](https://p5.ssl.qhimg.com/t01b0af3bd07954304f.png)](https://p5.ssl.qhimg.com/t01b0af3bd07954304f.png)

勒索提示文本文件RETURN FILES.txt，内容如下所示：

[![](https://p2.ssl.qhimg.com/t0136963370a8fee821.png)](https://p2.ssl.qhimg.com/t0136963370a8fee821.png)

黑产团伙留下了两个QQ邮箱地址：

[3442516480@qq.com](mailto:3442516480@qq.com)<br>[1169309366@qq.com](mailto:1169309366@qq.com)

此前我写过一篇文章，介绍Phobos勒索病毒，它是一款与CrySiS勒索病毒非常相似的勒索病毒，为啥这款勒索病毒是CrySiS，而不是Phobos呢?

通过动态调试样本，此勒索病毒先分配一段内存空间，如下所示：

[![](https://p4.ssl.qhimg.com/t01982836258da938db.png)](https://p4.ssl.qhimg.com/t01982836258da938db.png)

解密出shellcode代码，如下所示：

[![](https://p2.ssl.qhimg.com/t015b119415f4f67d58.png)](https://p2.ssl.qhimg.com/t015b119415f4f67d58.png)

再转跳到相应的shellcode代码处，如下所示：

[![](https://p2.ssl.qhimg.com/t017699c9f11d8a0c43.png)](https://p2.ssl.qhimg.com/t017699c9f11d8a0c43.png)

通过shellcode，再次分配相应的内存空间，如下所示：

[![](https://p3.ssl.qhimg.com/t0126c9b9295f61de44.png)](https://p3.ssl.qhimg.com/t0126c9b9295f61de44.png)

然后解密出勒索病毒核心Payload代码，如下所示：

[![](https://p5.ssl.qhimg.com/t01557f79b90408ebcd.png)](https://p5.ssl.qhimg.com/t01557f79b90408ebcd.png)

使用IDA打开勒索病毒核心Payload，如下所示：

[![](https://p5.ssl.qhimg.com/t01a4569c1046b90fb6.png)](https://p5.ssl.qhimg.com/t01a4569c1046b90fb6.png)

如果你之前分析过CrySiS病毒样本，一看就知道这是CrySiS的勒索病毒的入口代码特征，不是Phobos勒索病毒，Phobos勒索病毒的入口代码特征，应该如下所示：

[![](https://p4.ssl.qhimg.com/t0170cdfdd57cf954c9.png)](https://p4.ssl.qhimg.com/t0170cdfdd57cf954c9.png)

不要问我为什么Phobos和CrySiS的入口特征是这样的，很多东西只有你去真正花时间去深入分析研究，才会懂，好了不扯远了，其实最简单的方法就是你拿几个Phobos和CrySiS的不同变种去分析就知道了，把这款勒索核心Payload代码，与此前的CrySiS的Payload进行代码对比，如下所示：

[![](https://p5.ssl.qhimg.com/t01194fbd3eba2a316e.png)](https://p5.ssl.qhimg.com/t01194fbd3eba2a316e.png)

与之前的CrySiS勒索病毒代码相似度高达99%，可以确认此勒索病毒为CrySiS勒索病毒的变种样本

最近一两年针对企业的勒索病毒攻击越来越多，不断有朋友通过微信联系我，给我反馈各种勒索病毒相关信息，在此感谢各位朋友，大部分勒索病毒还不能解密，希望企业做好相应的勒索病毒防御措施，提高员工的安全意识，不要以为没了中勒索就没事，事实上黑产每天都在不断发起勒索攻击，不要等到中了勒索病毒才知道安全的重要性

本文转自：[安全分析与研究](https://mp.weixin.qq.com/s/O3j1E59AOc53VJF1wIP8aw)

> 原文链接: https://www.anquanke.com//post/id/170840 


# Lucky双平台勒索者解密分析


                                阅读量   
                                **152380**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t015477c66c5d389980.png)](https://p4.ssl.qhimg.com/t015477c66c5d389980.png)



## 0x0概况

Lucky是一种超强传播能力的恶意代码软件家族。其功能复杂，模块较多，能够利用多种漏洞组合和进行攻击传播。

含有Windows和Linux双平台攻击模块，加密算法使用RSA+AES算法，攻击完成最后利用中毒计算机进行挖矿，勒索等。

本文只分析其中的加密勒索模块部分，主要实现其加密后文件的解密，至于其他攻击模块，可参考文章后边提供的其他文章。



## 0x1加密分析

判断条件部分：勒索病毒会遍历全盘文件，加密固定扩展名的文件。

### 0x0概况

### 0x1加密分析

## 0x2解密思路

病毒全部分析完就可以找到其加密算法中的漏洞用以解密,以下提供三种方案的思路：

（1）如果勒索病毒进程还在运行，则直接从0x610A30地址处提取Key用于解密。

（2）如果勒索病毒进程不存在了，或者没有提取到Key，则尝试碰撞Key。

        如果已知①某文件加密前的部分数据，②这个文件被加密后的那部分数据，③勒索病毒大概的爆发时间

（3）同上，没有提取到Key，尝试碰撞。如果未知加密前文件数据。则尝试用RAR，DOC等文件开始必须的数据作对比。

以上说的方法都不需要去利用病毒中的RSA算法解密key(文件末尾添加的512字节),也就简单了许多.那么详细说下第二种：

我这里准备的数据是，1.源文件 BOOTSECT.BAK ；2.被加密的文件 [nmare@cock.li]BOOTSECT.BAK.kDeLBN1WSg5DKZQjw7OhSOcmumYeDnN11eIAiIc1.lucky。

具体碰撞方法就是，生成随机字符串+固定字符串，计算出KEY，尝试去解密[nmare@cock.li]BOOTSECT.BAK.kDeLBN1WSg5DKZQjw7OhSOcmumYeDnN11eIAiIc1.lucky文件中的前16个字节，如果解密的内容与源文件BOOTSECT.BAK中前16个字节中的内容相同，则判断为有效Key，可以去尝试解密其他文件。

提一下第三种：

第三种实际与第二种思路一样，只不过是对比源文件数据与加密文件数据的时候，源文件如果是RAR,DOC等文件，其开始处的源数据直接已知，不许要再有被加密的前的源文件。

比如RAR压缩文件，开始必有RAR!…的字符串可作为对比源。

[![](https://p4.ssl.qhimg.com/t01b17bc64e69c817b4.png)](https://p4.ssl.qhimg.com/t01b17bc64e69c817b4.png)

生成Key的思路如图：

[![](https://p5.ssl.qhimg.com/t01680b6f1f75ccc8ef.png)](https://p5.ssl.qhimg.com/t01680b6f1f75ccc8ef.png)

部分测试代码：

[![](https://p4.ssl.qhimg.com/t01a5b8066364b29708.png)](https://p4.ssl.qhimg.com/t01a5b8066364b29708.png)

[![](https://p4.ssl.qhimg.com/t015f4b06f39e00814c.png)](https://p4.ssl.qhimg.com/t015f4b06f39e00814c.png)

## 0x3解密实现

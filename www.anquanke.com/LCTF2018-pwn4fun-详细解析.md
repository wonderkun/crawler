> 原文链接: https://www.anquanke.com//post/id/164633 


# LCTF2018-pwn4fun-详细解析


                                阅读量   
                                **166661**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t01b30d90d52903d5ef.jpg)](https://p5.ssl.qhimg.com/t01b30d90d52903d5ef.jpg)



## LCTF-pwn4fun-详细解析

LCTF真的有一点劝退的意思。。。膜一波出题人，当时自己没有做出来，和大佬交流了一下思路之后会了。感觉题目是很新奇的，因为有点像是现实环境中逻辑漏洞利用。



## 程序分析

题目的代码很多这里列出一些主要的

### <a name="%E8%BF%90%E8%A1%8C%E5%9B%BE"></a>运行图

[![](https://p3.ssl.qhimg.com/t012cb344ed571d413c.png)](https://p3.ssl.qhimg.com/t012cb344ed571d413c.png)

### <a name="main"></a>main

[![](https://p4.ssl.qhimg.com/t015151feb68e69b418.png)](https://p4.ssl.qhimg.com/t015151feb68e69b418.png)<br>
我这里标出了一些函数的大概名字，这里说一些简单的函数首先admin是把字符串admin先放在一个地址里，然后接下来name函数就是输入自己的名字，就如上面运行图片展示的，然后开始游戏

### <a name="dont_know"></a>dont_know

[![](https://p3.ssl.qhimg.com/t010d7021bbc704ee97.png)](https://p3.ssl.qhimg.com/t010d7021bbc704ee97.png)<br>
这个函数刚开始标为dont_know是因为我开始看的时候并不知道是什么意思。。然后就继续看了下面，现在我们来看看这个函数,首先我这里将一个变量命名为了file_neme因为我发现它把值赋给了file，然后后面有一个openfile的操作，感觉这里有些不对劲，可能可以有些打开flag文件的操作，因为有一个congratulate的字符串在这里，但是这里并没有被怎么调用

### <a name="%E8%BE%93%E5%85%A5%E6%AF%94%E8%BE%83%E5%87%BD%E6%95%B0"></a>输入比较函数

[![](https://p5.ssl.qhimg.com/t01ebca14670006b676.png)](https://p5.ssl.qhimg.com/t01ebca14670006b676.png)<br>
这里会有一个比较让我们输入不能等于admin

### <a name="menu"></a>menu

[![](https://p2.ssl.qhimg.com/t01b55339b2f5bdbdd4.png)](https://p2.ssl.qhimg.com/t01b55339b2f5bdbdd4.png)<br>
这里有4个操作数，首先是do something，然后是do something again，然后是do something else，然后是do nothing，这里do nothing会执行一个退出的操作.接下里具体讲讲其他选项

### <a name="choose%201%20&amp;%20do%20something"></a>choose 1 &amp; do something

[![](https://p0.ssl.qhimg.com/t01002d785fc97eda9c.png)](https://p0.ssl.qhimg.com/t01002d785fc97eda9c.png)<br>
可以发现它对一个byte类型数进行了一个赋值，这里原来是一个数字，但是我发现这个是在可见字符的范围里所以我直接r了一下，进行了一个转换。看看这个地方并没有什么bug额。

### <a name="choose%202%20&amp;%20do%20something%20again"></a>choose 2 &amp; do something again

[![](https://p0.ssl.qhimg.com/t0185bbbcfa4348d9a9.png)](https://p0.ssl.qhimg.com/t0185bbbcfa4348d9a9.png)<br>
这里和第一个操作时差不多的，所以就不多解释了，也是对那个位置进行一个赋值，先记住这个字符串以为之后可能会用到。接下里的3就不进行分析了，是差不多的函数，无非就是blood不相同

### <a name="%E6%9C%80%E5%90%8E%E4%B8%80%E4%B8%AA%E5%87%BD%E6%95%B0"></a>最后一个函数

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01a494c4f063f5b52b.png)<br>
这里有一个很明显的格式化字符串漏洞，但是我怎么也做不到成功的赢，在上面blood循环之中，这个游戏类似于卡牌游戏一样，可以进攻然后可以放弃此轮回合，也可以吃了对方的牌，当然对于题目本身来说肯定是会有丢弃卡牌的环节，这里就是一个可以利用的地方了

### <a name="%E6%BA%A2%E5%87%BA%E7%82%B9%E5%9C%A8%E4%B8%A2%E7%89%8C%E5%A4%84"></a>溢出点在丢牌处

[![](https://p5.ssl.qhimg.com/t01af6ff09503a3277e.png)](https://p5.ssl.qhimg.com/t01af6ff09503a3277e.png)<br>
这里在第二次丢牌的时候没有检查下表所以可以直接进行一个数组越界的覆盖



## 动态调试

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](./fl4g.png)这个地方是我用ida动态调试的时候发现的，在admin的情况下会进行一个open file的操作，可是open出来的是一个。。。 [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](./fake.png)

这里可以发现是一个假的flag。。。太服气了这一点了，所以我们还是要继续寻找。继续寻找的过程中可以发现在丢牌的时候有一个下表溢出会让我们可以覆盖到flag那个地方，这也就用到了

这个地方可以进行一个下表越界-5对4进行一个a覆盖

### <a name="%E6%80%9D%E8%B7%AF%E5%88%86%E6%9E%90"></a>思路分析

进入第二个选项的丢牌然后让下标进行一个溢出，溢出-5，进行一个flag的布置然后就可以读取flag了，当让这里的admin需要加上‘’将9个字符串填满

### <a name="EXP"></a>EXP

ps:这里请教了一下lm0963，膜一波，一个人拿了两个pwn-fd



## 总结

这几次的比赛在pwn上会有很多的新题，其中最大的感受就是对pwn手的逆向要求更高的了，就比如湖湘杯的pwn1，代码量也很大，而还有这个lctf的这道题目需要先知道程序的功能才能pwn。还有之前出现过的vmpwn。。。

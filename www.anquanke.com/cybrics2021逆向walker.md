> 原文链接: https://www.anquanke.com//post/id/248541 


# cybrics2021逆向walker


                                阅读量   
                                **23743**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t01707e748ca3b004aa.png)](https://p0.ssl.qhimg.com/t01707e748ca3b004aa.png)



## ida分析

### <a class="reference-link" name="1.%E5%88%9D%E6%AC%A1%E5%88%86%E6%9E%90"></a>1.初次分析

[![](https://p4.ssl.qhimg.com/t010a90bcab3dea5326.png)](https://p4.ssl.qhimg.com/t010a90bcab3dea5326.png)

看到有一个start_check函数，跟进分析

[![](https://p1.ssl.qhimg.com/t01d0794f8a141dd1c9.png)](https://p1.ssl.qhimg.com/t01d0794f8a141dd1c9.png)

看到有一个global_flag数组，不过可以发现是个假flag。

[![](https://p1.ssl.qhimg.com/t01c504c0e115d77c82.png)](https://p1.ssl.qhimg.com/t01c504c0e115d77c82.png)

### <a class="reference-link" name="2.%E5%86%8D%E5%88%86%E6%9E%90"></a>2.再分析

[![](https://p3.ssl.qhimg.com/t013f8b276961974c80.png)](https://p3.ssl.qhimg.com/t013f8b276961974c80.png)

再函数栏里有一些名字比较可疑的函数

[![](https://p5.ssl.qhimg.com/t012144b68d20eaaa3f.png)](https://p5.ssl.qhimg.com/t012144b68d20eaaa3f.png)

看到这里可以确定这里才是真正的验证入口



## gdb调试

在这里对每个函数的单独分析的时候可能会有点不完整，在写的时候我想尽可能保留本人当时做题时分析的思路和理由，而不是以一个上帝视角去分析。

### <a class="reference-link" name="check_substr%E5%87%BD%E6%95%B0"></a>check_substr函数

这个函数名看着就很可疑，就先那它开刀了

[![](https://p4.ssl.qhimg.com/t019400fe4d2a07b927.png)](https://p4.ssl.qhimg.com/t019400fe4d2a07b927.png)

第一时间看到这个(v5^a1[a2+i]!=v7[i])再结合函数名，十有八九是验证逻辑了。<br>
有2个比较用到的数组一个是map[]，一个是strings[]

[![](https://p0.ssl.qhimg.com/t011fd1a5cadb907721.png)](https://p0.ssl.qhimg.com/t011fd1a5cadb907721.png)

[![](https://p0.ssl.qhimg.com/t014046d2d69b6ca402.png)](https://p0.ssl.qhimg.com/t014046d2d69b6ca402.png)

这里一开始的时候也不知道要输入什么，就输入cybrics`{`aaaa试一下。现在看回来这个尝试的输入，成为了破局的关键。<br>
断点下在比较逻辑之前，这样可以在调试的时候看到v5,a1[a2+i],v7[]的值。

[![](https://p4.ssl.qhimg.com/t01aedd056032944548.png)](https://p4.ssl.qhimg.com/t01aedd056032944548.png)

可以知道a1[]就是’c’之后的字符串了，v5的值可以通过异或后再异或来倒推，这里求出v5为0x61，刚好为map[]的第一个值，而v7[]为字符串数组的第二个值。<br>
然后继续运行程序，程序就结束了，证实了确实是验证逻辑。并且有个T5Excrption的函数，猜测这个函数跟退出有关，并且上面也有一个T5Excrption的函数。

利用py求出正确的字符串”REUaG”，再次输入。几次运行后发现比较完后需要继续输入。

[![](https://p3.ssl.qhimg.com/t0106cb2a8356d3f2df.png)](https://p3.ssl.qhimg.com/t0106cb2a8356d3f2df.png)

输入”caaaa”测试

[![](https://p2.ssl.qhimg.com/t01d66b7d20bd13bdb3.png)](https://p2.ssl.qhimg.com/t01d66b7d20bd13bdb3.png)

发现v5的值还是0x61，但是v7[]的字符串变成了字符串数组的第三个值。

可以得到以下猜测：<br>
1.v5=map[10 * x_pos + y_pos]中的x和y是可以通过某些操作改变的。<br>
2.而MOVES的值在每次进入这个函数的时候会加一。<br>
3.T5Excrption的函数跟程序退出有关。<br>
4.利用ida的函数关联功能，发现函数是从make_move函数调用的。

### <a class="reference-link" name="process_move%E5%87%BD%E6%95%B0"></a>process_move函数

[![](https://p5.ssl.qhimg.com/t0176081f6d3c44c67e.png)](https://p5.ssl.qhimg.com/t0176081f6d3c44c67e.png)

首先有4个对应关系：<br>
u:T6Exception(x_pos-1,y_pos)<br>
r:T6Exception(x_pos,y_pos+1)<br>
d:T6Exception(x_pos+1,y_pos)<br>
l:T6Exception(x_pos,y_pos-1)

[![](https://p0.ssl.qhimg.com/t018bc588244570b8b5.png)](https://p0.ssl.qhimg.com/t018bc588244570b8b5.png)

看到这3个if的判断，立刻有感觉了。当时认为是一个10×10的迷宫，并且题目名walker。<br>
再结合check_cubstr函数中对map[]的判断，得出以下迷宫。

[![](https://p1.ssl.qhimg.com/t01b484adfa4b5a3472.png)](https://p1.ssl.qhimg.com/t01b484adfa4b5a3472.png)

把map[x_pos * 10 + y_pos]&amp;1==1的值都标出来。

然后在根据那4个对应关系，u代表up(想上移动一格)，d代表down(向下移动一格)，l代表left(向左移动一格)，r代表right(向右移动一格)。

但是这个迷宫也没有什么规律可言，于是就进入了苦逼的人工爆破时间，顺便找规律。

最终得到以下路径：dddrruurrrrddddllllddrrrrrddlllllll。(还好在每一个点只有唯一选择，不然也没耐心爆下去了，并且最后map[]移动到0x66的时候输入什么会退出程序，又把思路断了)

利用ida的函数关联功能，发现函数也是从make_move函数调用的。

### <a class="reference-link" name="make_move%E5%87%BD%E6%95%B0"></a>make_move函数

[![](https://p3.ssl.qhimg.com/t01a4d4dece687ef48f.png)](https://p3.ssl.qhimg.com/t01a4d4dece687ef48f.png)

反汇编码给的信息有点少，所以打算通过gdb和汇编码来分析函数的功能。<br>
不过看到++MOVES;更加肯定进入check_substr函数要经过make_move函数。并且有个jmp rax的汇编，猜测应该是实现了一个选择器功能。

选择在check_substr函数和process_move函数的入口下断点，并进行调试。

[![](https://p5.ssl.qhimg.com/t013a5a540c4caa0c1d.png)](https://p5.ssl.qhimg.com/t013a5a540c4caa0c1d.png)

发现程序断在了check_substr函数入口。<br>
继续运行

[![](https://p5.ssl.qhimg.com/t0181fa5518fa554d22.png)](https://p5.ssl.qhimg.com/t0181fa5518fa554d22.png)

程序断在了process_move函数入口。<br>
这时候可以肯定make_move函数根据输入的字符来跳转到不同的函数。

分析jmp rax附近的汇编

[![](https://p0.ssl.qhimg.com/t010d1712ac00d9f71c.png)](https://p0.ssl.qhimg.com/t010d1712ac00d9f71c.png)

[![](https://p1.ssl.qhimg.com/t014d33feee00bcb4a8.png)](https://p1.ssl.qhimg.com/t014d33feee00bcb4a8.png)

发现一个类似偏移的表，由1个0xffffe7f7,4个0xffffe7b7,若干个0xffffe861,1个0xffffe82f构成。

调试分析表的作用

[![](https://p1.ssl.qhimg.com/t01e07b8c80d7a8668b.png)](https://p1.ssl.qhimg.com/t01e07b8c80d7a8668b.png)

可以看到表的取值是根据输入字符减去0x63后的值决定的，这里输入字符c，返回的值是表的第一个值。<br>
那可以通过调试分析得到以下对应关系<br>
0xffffe7f7：check_substr<br>
0xffff7b7：process_move<br>
0xffff861：什么都不做，需要继续输入(但是每输入一次MOVES都会自加一)<br>
0xffff82f：不清楚什么功能，但是程序会退出

在看汇编的时候发现在make_move函数有一个这种东西。

[![](https://p0.ssl.qhimg.com/t015e090300e1dd5a81.png)](https://p0.ssl.qhimg.com/t015e090300e1dd5a81.png)

提示输入即为flag的内容。



## 综合分析

### <a class="reference-link" name="%E8%BF%B7%E5%AE%AB%E8%B7%AF%E5%BE%84%E5%92%8Ccheck%E5%87%BD%E6%95%B0"></a>迷宫路径和check函数

把路径和符合check函数的map[]值结合

[![](https://p5.ssl.qhimg.com/t017c86837ce8710455.png)](https://p5.ssl.qhimg.com/t017c86837ce8710455.png)

得到其中红色字为二者重合的地方，猜测flag的逻辑为当移动到map的值为0x61,0x45,0x49,0x71时执行check_substr函数和路径的结合

[![](https://p0.ssl.qhimg.com/t01fb52c51c52fd940b.png)](https://p0.ssl.qhimg.com/t01fb52c51c52fd940b.png)

到这里为止还有一个当输入为字符f的时候的功能还没有弄明白，试一下。

[![](https://p2.ssl.qhimg.com/t01064710b136756bf8.png)](https://p2.ssl.qhimg.com/t01064710b136756bf8.png)

成功get flag。



## 感想

当时做出来这道题的时候，可以说是激动到不行。学了这么久，有一种守得云开见月明的感觉，感觉自己一直以来的努力终于有了结果。可能这种通过一步一步调试分析程序，对程序的感觉从一开始什么都不知道的黑盒，到最后清楚明白程序怎么运行的白盒，才是逆向这个方面吸引我的魅力

> 原文链接: https://www.anquanke.com//post/id/185964 


# FastJson拒绝服务漏洞分析


                                阅读量   
                                **537706**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">5</a>
                                </b>
                                                                                    



![](https://p1.ssl.qhimg.com/t01c9994900763f71eb.png)



作者:fnmsd[@360](https://github.com/360)云安全

## 前言

从[@badcode](https://github.com/badcode)师傅那里知道了这么漏洞，尝试着分析复现一下，影响范围fastjson&lt;=1.2.59。

感谢[@pyn3rd](https://github.com/pyn3rd)师傅对OOM机制的讲解。

该漏洞会导致java进程的占用内存迅速涨到JVM允许的最大值（-Xmx参数，默认为1/4物理内存大小），并且CPU飙升。

该漏洞并不能直接打挂java进程，但是可能由于java进程占用内存过大，导致被系统的OOM Killer杀掉。



## 补丁

github上的diff：

![](https://p0.ssl.qhimg.com/t012ec80aa4b2c97543.png)

scanString针对JSON中x字符的处理，加入了判断后两个字符是否为hex字符，不为hex字符，直接退出。

![](https://p0.ssl.qhimg.com/t01b2fb36b921c3b9f8.png)

还有isEOF方法也进行了逻辑完善。



## 测试代码

简化了一下，原版的可以看引用里的链接：

```
import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONException;

public class fastjsonDos `{`
    public static void main(String[] args)`{`
        //`{`"a":"x
        //漏洞是由于fastjson处理字符串中x这种HEX字符表示形式出现的问题。
        String DEATH_STRING = "`{`"a":"\x";//输入字符串长度为8
        try`{`
            Object obj = JSON.parse(DEATH_STRING);
            System.out.println(obj);
        `}`catch (JSONException ex)`{`
            System.out.println(ex);
        `}`
    `}`
`}`

```

使用fastjson 1.2.59+jdk8u20，测试机内存20GB。



## 整体流程分析

根据补丁可以看出，是对JSONLexerBase类中ScanString方法的switch中的case ‘x’分支进行了修改(x这种Hex字符的处理部分)，所以在1.2.59的该部分进行下断点。

![](https://p5.ssl.qhimg.com/t011871dd68a3b4774f.png)

跟入next方法，到了JSONScanner类的next方法：

![](https://p5.ssl.qhimg.com/t01913830f21ecb23dc.png)

可以看到逻辑，会对bp进行+1操作并赋给index，如果index&gt;=this.len(JSON的长度)就会返回EOI，否则返回文本内容。

![](https://p4.ssl.qhimg.com/t01056d8781910ed8c1.png)

EOI=0x1A

回到scanString函数，经过了两次next,bp已经为9，而输入的字符串长度为8。

继续往下走，跟入putChar函数：

![](https://p1.ssl.qhimg.com/t01d7e83087a1f18c3d.png)

如果sp与sbuf数组长度相等，就扩张sbuf数组长度（大小翻倍，所以看起来OOM的位置应该就在这）

回到scanString中，继续往下走，发现回到了scanString的开头，刚才的代码部分都是在一个死循环当中：

![](https://p3.ssl.qhimg.com/t01c9a89396af8afddf.png)

由于此时bp已经大于输入的字符串长度，此时next()会返回EOI(0x1A)不等于双引号，并进入到ch==EOI的分支中，跟入isEOF函数：

![](https://p4.ssl.qhimg.com/t011131a081d57b13f8.png)

`bp==len`和`ch==EOI&amp;&amp;bp+1==len`认为是EOF，但此时bp=10 len=8，后面再调用next方法bp只可能更大，永远不满足isEOF的条件，所以上面的`putChar(EOI)`会无限的执行，sBuf不断扩大，直到OOM。

emm，但是实际测试的时候还是有点差别的。



## 单线程运行没OOM异常

首次运行代码很快就报了这么一个异常：

![](https://p3.ssl.qhimg.com/t012e4c52bb9b0c08e8.png)

NegativeArraySizeException，数组长度为负值异常,并没有OOM。

在idea中下了一个异常断点到NegativeArraySizeException上,断点断在了putChar数组空间扩展的位置：

![](https://p2.ssl.qhimg.com/t01ba12ad7a41eaed19.png)

此时sbuf的长度为1073741824（1G的大小），而sbuf.length的类型为int型，int型最大为2147483647。

而1073741824×2= 2147483648，正好大1，所以下溢出了：

![](https://p4.ssl.qhimg.com/t01e096cc768b345306.png)

此时内存占用3.3GB左右。

![](https://p2.ssl.qhimg.com/t0198868a58adc846a4.png)

通过多方查询，java的默认最大允许内存最大物理内存的1/4，我这应该就是5GB左右，此时还没有到OOM的标准，反而由于下溢出先触发了NegativeArraySizeException这个异常。



## 多线程运行触发OOM

既然单的不行就来个多的，稍微改下代码，改个多线程的：

```
import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONException;

public class fastjsonDos1 implements Runnable`{`
    public static void main(String[] args)  `{`

        new Thread(new fastjsonDos1()).start();
        new Thread(new fastjsonDos1()).start();
//        new Thread(new fastjsonDos1()).start();
//       new Thread(new fastjsonDos1()).start();
//        new Thread(new fastjsonDos1()).start();

    `}`

    public void run() `{`
        String DEATH_STRING = "`{`"a":"\x";
        try`{`
            Object obj = JSON.parse(DEATH_STRING);
            System.out.println(obj);
        `}`catch (JSONException ex)`{`
            System.out.println(ex);
        `}`
    `}`
`}`

```

我的测试机20GB内存两个线程就OOM了：

![](https://p1.ssl.qhimg.com/t01cb24b9e62483c64c.png)

可以看到Thread1先OOM，Thread0缺依然是下溢出问题，所以虽然线程OOM了，java进程并没有挂掉。

![](https://p2.ssl.qhimg.com/t01d8e6a7f956e21906.png)

写了一个简单的SpringBoot应用做测试，使用burp以10线程进行访问，可以发现虽然一直报OOM异常，但是java进程却没有挂掉，内存最后稳定在4GB多（略小于-Xmx）使不再触发漏洞，占用内存也不会再减小。

顺便CPU飙升：

![](https://p5.ssl.qhimg.com/t01bbd15915b7373045.png)

有想做实验的朋友可以尝试着将运行java的-Xmx参数改的大大，然后再运行感受一下。（老实人的微笑）



## 有关OOM

Java的OutOfMemoryError是JVM内部的异常，是一个可捕获异常，并不会直接导致java进程被Kill掉，顶多线程挂掉。

Linux下当应用程序内存超出内存上限时，会触发OOM Killer机制以保持系统空间正常运行，哪个进程被点名Kill是通过linux/mm/oom_kill.c中oom_badness进行算分选择的，并且可以通过设定oom_adj 来调节其被Kill的可能性。

所以，java默认最大1/4物理内存占用，不太容易造成系统的OOM的（当然你系统里其他的进程是吃内存怪当我没说）。

但是很多关于java OOM异常的解决文章中建议将最大值改为不超过物理内存的80%，此时就有可能造成内存占用过多，导致被系统Kill掉。



## 参考

[https://github.com/alibaba/fastjson/commit/995845170527221ca0293cf290e33a7d6cb52bf7#diff-aa8d9d6e56964418428ff59fb887afae](https://github.com/alibaba/fastjson/commit/995845170527221ca0293cf290e33a7d6cb52bf7#diff-aa8d9d6e56964418428ff59fb887afae)

[https://github.com/alibaba/fastjson/commit/80b7b1e6d57a722f7cca549540394c3072ad8ecb](https://github.com/alibaba/fastjson/commit/80b7b1e6d57a722f7cca549540394c3072ad8ecb)

[https://github.com/Omega-Ariston/fastjson/blob/b44900e5cc2a0212992fd7f8f0b1285ba77bb35d/src/test/java/com/alibaba/json/bvt/issue_2600/Issue2689.java](https://github.com/Omega-Ariston/fastjson/blob/b44900e5cc2a0212992fd7f8f0b1285ba77bb35d/src/test/java/com/alibaba/json/bvt/issue_2600/Issue2689.java)

[https://blog.csdn.net/liukuan73/article/details/43238623](https://blog.csdn.net/liukuan73/article/details/43238623)

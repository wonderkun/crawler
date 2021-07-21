> 原文链接: https://www.anquanke.com//post/id/159554 


# 奇淫技巧之突破Runtime.exec限制获取shell 命令执行环境


                                阅读量   
                                **265514**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t01c758d15d94c43555.jpg)](https://p1.ssl.qhimg.com/t01c758d15d94c43555.jpg)

> 严正声明：本文仅限于技术讨论与学术学习研究之用，严禁用于其他用途（特别是非法用途，比如非授权攻击之类），否则自行承担后果，一切与作者和平台无关，如有发现不妥之处，请及时联系作者和平台

## 0x00. 前言

在一次内部安全测试中，碰到个java 站点，有一处任意代码执行漏洞，还可以回显，心理顿时美滋滋，但是当我执行稍微复杂点shell 命令的时候，发现回显明显不对，执行`ls -l /opt` 和 `ls -l /opt/ |grep tomcat` 两个命令输出结果完全一样，`grep` 完全没有生效，处于好奇，找到了相关开发，看了下漏洞问题出的源码，原来是参数没有过滤，直接丢进`Runtime.getRuntime().exec()`中执行了。虽然可以通过远程download 脚本直接都给`Runtime.exec()`执行绕过这个限制，但是出于好奇心，我google不少资料，查阅一番资料之后，终于找到了问题的原因，然后发现了个绕过限制的小技巧并获取完整的shell 执行命令环境，详文如下。



## 0x01. 先介绍线下Runtime类执行外部命令的方法介绍

要运行JVM中外的程序，`Runtime`类提供了如下方法：

[![](https://p2.ssl.qhimg.com/t01543e0d493546a8e7.png)](https://p2.ssl.qhimg.com/t01543e0d493546a8e7.png)

简单解释如下:

`exec(String command)<br>
在单独的进程中执行指定的字符串命令。

exec(String[] cmdarray)<br>
在单独的进程中执行指定命令和变量。

exec(String[] cmdarray, String[] envp)<br>
在指定环境的独立进程中执行指定命令和变量。

exec(String[] cmdarray, String[] envp, File dir)<br>
在指定环境和工作目录的独立进程中执行指定的命令和变量。

exec(String command, String[] envp)<br>
在指定环境的单独进程中执行指定的字符串命令。

exec(String command, String[] envp, File dir)<br>
在有指定环境和工作目录的独立进程中执行指定的字符串命令。`

0x00. 中涉及的案例的环境就是第一个`exec(String command)` ，直接执行外部传进来的命令字符串，`Runtime.getRuntime().exec()` 执行外部命令的原理就是fork一个单独的进程，然后直接执行这个命令。`exec(String command)`这个方法是没法指定shell为命令上下文环境，所以这也就解释了为啥

`ls -l /opt` 和 `ls -l /opt |grep tomtcat` 结果一样

因为 `|` 是shell环境下的管道命令，只有shell的执行上下文环境才识别，直接fork进程执行ls 命令是不识别 `|`、`&gt;`重定向等shell中的复杂命令

如何突破exec() 无shell上下文执行环境限制获取完整shell执行环境呢，0x02 或有详细演示与分析



## 0x02. 突破限制之旅

我现在没了内部系统的那个测试环境，自己写了个演示代码，如下：

### 1、演示代码

[![](https://p0.ssl.qhimg.com/t01c22d6f47bfd6bd0c.png)](https://p0.ssl.qhimg.com/t01c22d6f47bfd6bd0c.png)

执行`javac Test.java` 进行编译就可以了

### 2、演示分析 ls -l /opt与ls -l /opt |grep anquanke 为啥结果一样

1） 执行 `ls -l /opt`

[![](https://p0.ssl.qhimg.com/t012588c6b0a33c4179.png)](https://p0.ssl.qhimg.com/t012588c6b0a33c4179.png)

2) 执行 `ls -l /opt |grep anquanke`

[![](https://p2.ssl.qhimg.com/t0106358e66dc297295.png)](https://p2.ssl.qhimg.com/t0106358e66dc297295.png)

提示 当前目录中文件或目录：|grep 不存在<br>
提示 当前目录下文件或目录：anquanke 不存在

为啥会这样呢？

这是因为`Runtime.exec`对传入的字符串是按照空格进行参数区分的，在这里<br>`|grep` 、`anquanke` 都被认为是文件或者目录，这里没有shell 上下文环境，管道命令 |是无法识别的

**注：** 这里要补充说明下，为啥`ls -l /opt |grep anquanke`会打印错误信息，因为代码就也把错误信息打印出来了，如果把错误信息去掉，那么两个命令执行结果就一样了

### 3、第一次突破尝试

既然`Runtime.exec()`无shell上下文环境，那么我调用sh -c 用sh直接执行命令，这下总可以了吧

1）执行 `java Test 'sh -c /usr/bin/ls -l /opt |grep anquanke'`

[![](https://p0.ssl.qhimg.com/t01a0c670f4a8d9cc84.png)](https://p0.ssl.qhimg.com/t01a0c670f4a8d9cc84.png)

但是上图的执行结果直接显示当前目录的内容，而不是`/opt` 目录下的

这是为啥？

`sh -c` 根据空格进行区分要执行的命令，如上图，执行的命令就是`/usr/bin/ls`,后面的参数都会被忽略(因为 `-l`、`/opt`、`|grep` 、`anquanke`都被认为是sh的参数)，要想让后面的 `-l` 之类参数也被识别，那就用引号括起来，如下

2）执行`java Test 'sh -c "/usr/bin/ls -l /opt |grep anquanke"'`

[![](https://p4.ssl.qhimg.com/t01fda35e41a68c4543.png)](https://p4.ssl.qhimg.com/t01fda35e41a68c4543.png)

我用引号将传递给sh 执行的命令括起来了啊，为啥还是报错呢？

这是因为`Rntime.exec()` 区分命令的依据是空格, 上面的命令传递给`Runtime.exec`后相当于相当于:

`sh -c '"/usr/bin/ls' '-l' '/opt|grep' 'anquanke'`

这就明白为啥会报错了吧

### 4、第二次尝试突破限制，获取完整shell执行环境

上面的突破之所以失败，是因为受限于`Runtime.exec` 依据空格划分参数的规则，sh -c 有时候不能直接执行复杂的命令，于是想到可以用管道传递给sh自身然后间接执行复杂命令嘛

于是有了下面的突破命令：

`java Test 'sh -c $@|sh 0 echo /usr/bin/ls -l /opt|grep anquanke'`

[![](https://p3.ssl.qhimg.com/t016d028410e3cab301.png)](https://p3.ssl.qhimg.com/t016d028410e3cab301.png)

解释下为啥这样就行

`sh -c $@|sh 0 echo /usr/bin/ls -l /opt|grep anquanke`

这个命令字符串传给`Runtime.exec()`之后，按照`Runtime.exec` 依据空格划分参数的规则，命令就变成：

`sh -c '$@|sh' '0' 'echo' '/usr/bin/ls' '-l' '/opt|grep' 'anquanke'`

就相当于：

[![](https://p1.ssl.qhimg.com/t019aa17439b7f39c22.png)](https://p1.ssl.qhimg.com/t019aa17439b7f39c22.png)

这个要补充下知识点了： `sh -c 'command' x1 x2 x3`

x1 被认为是脚本名称，相当于$0, x2、x3 相当于 $1、$2

命令 `sh -c '$@|sh' 0 echo /usr/bin/ls -l /opt|grep anquanke`

中的 0 可以换成任意名称 ，比如xx:

`sh -c '$@|sh' xx echo /usr/bin/ls -l /opt|grep anquanke`

[![](https://p5.ssl.qhimg.com/t0194c5af3a056ac26a.png)](https://p5.ssl.qhimg.com/t0194c5af3a056ac26a.png)

在shell 语法中 $@ 表示所有传递过来的位置参数，不包括$0, $0代表脚本名称

所以`sh -c $@|sh xx echo /usr/bin/ls -l /opt|grep anquanke`

这里的$@ 就相当于 `echo /usr/bin/ls -l /opt|grep anquanke`

最终就相当于执行如下命令

`sh -c 'echo "/usr/bin/ls -l /opt|grep anquanke"|sh'`

[![](https://p3.ssl.qhimg.com/t01e5150c5ab17a9cba.png)](https://p3.ssl.qhimg.com/t01e5150c5ab17a9cba.png)

### 5、搞个shell吧，不然这样收尾稍显突兀

[![](https://p0.ssl.qhimg.com/t0189043fb6d9393137.png)](https://p0.ssl.qhimg.com/t0189043fb6d9393137.png)<br>[![](https://p1.ssl.qhimg.com/t01d286f5004044ebbd.png)](https://p1.ssl.qhimg.com/t01d286f5004044ebbd.png)



## 0x03. 总结

分析完就一个字爽, 学到了不少东东哈哈



## 0x04. 参考资料

[http://hg.openjdk.java.net/jdk7/jdk7/jdk/file/tip/src/solaris/classes/java/lang/UNIXProcess.java.linux](http://hg.openjdk.java.net/jdk7/jdk7/jdk/file/tip/src/solaris/classes/java/lang/UNIXProcess.java.linux)<br>[https://www.jianshu.com/p/af4b3264bc5d](https://www.jianshu.com/p/af4b3264bc5d)

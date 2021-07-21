> 原文链接: https://www.anquanke.com//post/id/243329 


# Java 命令执行之我见


                                阅读量   
                                **106252**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t014a5712b5ab1dbd3e.png)](https://p2.ssl.qhimg.com/t014a5712b5ab1dbd3e.png)



## 前言

Java 代码审计当中，关于命令执行，我们主要关注的是函数 `Runtime.getRuntime().exec(command)` &amp;&amp; `new ProcessBuilder(command).start()`

在参数 command 可控的情况下，一般就会存在命令执行的问题，但是也会存在这种问题，有时候明明参数可控，但是无法成功执行命令，以及复杂的shell 命令，例如带有 `|` 、`&lt;`、`&gt;`、`$` 等符号的命令没办法正常执行。

```
Command = "ping 127.0.0.1"+request.getParameter("cmd");
Runtime.getRuntime().exec(command);
```

这样的一段代码是存在命令注入漏洞的吗？粗略一看，存在命令执行函数，command 获取从外部传入的 cmd ，应该是存在命令注入漏洞的。但是并没有执行成功，并不存在命令执行漏洞。

```
import java.io.IOException;

public class linux_cmd `{`
    public static void main(String[] args) throws IOException `{`
        String cmd =new String(";echo 1 &gt; 1.txt");
        String Command = "ping 127.0.0.1"+cmd;
        Runtime.getRuntime().exec(Command);
        //Runtime.getRuntime().exec(new String[]`{`"/bin/sh", "-c", Command`}`);
    `}`
`}`
```

直接通过 `Runtime.getRuntime().exec(Command);` 没有成功创建 1.txt。通过 `Runtime.getRuntime().exec(new String[]`{`"/bin/sh", "-c", Command`}`);` 成功创建 1.txt。 于是尝试对 Runtime.getRuntime().exec(Command); 进行调试分析。

我们跟进 Runtime.getRuntime().exec() 发现会依据传入的参数类型，而选用不同的函数。

[![](https://p0.ssl.qhimg.com/t0181c16b1e1d1d863e.png)](https://p0.ssl.qhimg.com/t0181c16b1e1d1d863e.png)



## Runtime.getRuntime().exec(String command）

当传入的参数类型是 String ，会到 `Process exec(String command)` 这个构造方法进行处理，最后返回了 `exec(command, null, null);`

`java.lang.Runtime#exec(java.lang.String)`

[![](https://p0.ssl.qhimg.com/t01b19374f167a70125.png)](https://p0.ssl.qhimg.com/t01b19374f167a70125.png)

`java.lang.Runtime#exec(java.lang.String, java.lang.String[], java.io.File)`

[![](https://p2.ssl.qhimg.com/t017c00558c83ed55d8.png)](https://p2.ssl.qhimg.com/t017c00558c83ed55d8.png)

在这个地方我们注意到利用 StringTokenizer 对输入的 command 进行了处理

`java.util.StringTokenizer#StringTokenizer(java.lang.String)`

[![](https://p5.ssl.qhimg.com/t0135b644938cf0a5ac.png)](https://p5.ssl.qhimg.com/t0135b644938cf0a5ac.png)

会根据 `\t\n\r\f` 把传入的 command 分割

[![](https://p2.ssl.qhimg.com/t01e40173b4a1d4eea6.png)](https://p2.ssl.qhimg.com/t01e40173b4a1d4eea6.png)

`java.lang.Runtime#exec(java.lang.String[], java.lang.String[], java.io.File)`

[![](https://p3.ssl.qhimg.com/t01337b02b29439eb64.png)](https://p3.ssl.qhimg.com/t01337b02b29439eb64.png)

经过处理之后，最后实例化了 ProcessBuilder 来处理传入的 cmdarray。可以证实 Runtime.getRuntime.exec() 的底层实际上也是 ProcessBuilder。

跟进 ProcessBuilder 中的 start 方法

`java.lang.ProcessBuilder#start`

[![](https://p3.ssl.qhimg.com/t011baf2348ed41cb5f.png)](https://p3.ssl.qhimg.com/t011baf2348ed41cb5f.png)

ProcessBuilder.start 内部又调用了 ProcessImpl.start

[![](https://p4.ssl.qhimg.com/t0117cd4601a8a63d0e.png)](https://p4.ssl.qhimg.com/t0117cd4601a8a63d0e.png)

在 ProcessImpl.start 中 将 cmdarry 第一个参数 (cmdarry[0]) 当作要执行的命令，把后面的部分 (cmdarry[1:]) 作为命令执行的参数转换成 byte 数组 argBlock。

最后将处理好的参数传给 UNIXProcess

[![](https://p0.ssl.qhimg.com/t01b3efc2e0e613ab5b.png)](https://p0.ssl.qhimg.com/t01b3efc2e0e613ab5b.png)

`java.lang.UNIXProcess#UNIXProcess`

[![](https://p2.ssl.qhimg.com/t011fd5fe5e71a5b892.png)](https://p2.ssl.qhimg.com/t011fd5fe5e71a5b892.png)

我们看到当前断点的 pid 是 3229 , 这里确实启动了一个 ping 进程

[![](https://p3.ssl.qhimg.com/t01fca6ef3fa2e19832.png)](https://p3.ssl.qhimg.com/t01fca6ef3fa2e19832.png)

此时 prog 是要执行的命令 `ping` , argBlock 都是传给 ping 的参数 `127.0.0.1\x00;echo\x001\x00&gt;\x001.txt`

经过 StringTokenizer 对字符串的处理，命令执行的语义发生了改变，并不是最初设定的想法。



## Runtime.getRuntime().exec(String cmdarray[])

```
import java.io.IOException;

public class linux_cmd `{`
    public static void main(String[] args) throws IOException `{`
        String cmd =new String(";echo 1 &gt; 1.txt");
        String Command = "ping 127.0.0.1"+cmd;
        //Runtime.getRuntime().exec(Command);
        Runtime.getRuntime().exec(new String[]`{`"/bin/sh", "-c", Command`}`);
    `}`
`}`
```

我们传入数组，进行分析，因为直接传入的是数组，所以没有经过 StringTokenizer 对字符串的处理

`java.lang.Runtime#exec(java.lang.String[])`

[![](https://p4.ssl.qhimg.com/t01ff94c6d207ad79da.png)](https://p4.ssl.qhimg.com/t01ff94c6d207ad79da.png)

`java.lang.Runtime#exec(java.lang.String[], java.lang.String[], java.io.File)`

[![](https://p3.ssl.qhimg.com/t019cd4784c22aef458.png)](https://p3.ssl.qhimg.com/t019cd4784c22aef458.png)

`java.lang.UNIXProcess#UNIXProcess`

[![](https://p1.ssl.qhimg.com/t01cad40497baaac389.png)](https://p1.ssl.qhimg.com/t01cad40497baaac389.png)

此时 prog 是要执行的命令 `/bin/sh` , argBlock 都是传给 ping 的参数 `-c\x00"ping 127.0.0.1;echo 1 &gt; 1.txt"`



## 编码

[编码地址](http://www.jackson-t.ca/runtime-exec-payloads.html)

[![](https://p0.ssl.qhimg.com/t015c0dae128a4853c6.png)](https://p0.ssl.qhimg.com/t015c0dae128a4853c6.png)

```
import java.io.IOException;

public class linux_cmd `{`
    public static void main(String[] args) throws IOException `{`
        String Command = "bash -c `{`echo,cGluZyAxMjcuMC4wLjE7ZWNobyAxID50ZXN0LnR4dA==`}`|`{`base64,-d`}`|`{`bash,-i`}`";
        Runtime.getRuntime().exec(Command);
    `}`
`}`
```

`java.lang.Runtime#exec(java.lang.String)`

[![](https://p4.ssl.qhimg.com/t0141aee77404644073.png)](https://p4.ssl.qhimg.com/t0141aee77404644073.png)

`java.lang.Runtime#exec(java.lang.String, java.lang.String[], java.io.File)`

[![](https://p0.ssl.qhimg.com/t014ccc2a7c2b7c42fd.png)](https://p0.ssl.qhimg.com/t014ccc2a7c2b7c42fd.png)

`java.lang.UNIXProcess#UNIXProcess`

[![](https://p3.ssl.qhimg.com/t011866ba5a324760d2.png)](https://p3.ssl.qhimg.com/t011866ba5a324760d2.png)

此时 prog 是要执行的命令 `bash` , argBlock 都是传给 ping 的参数 `-c\x00`{`echo,cGluZyAxMjcuMC4wLjE7ZWNobyAxID50ZXN0LnR4dA==`}`|`{`base64,-d`}`|`{`bash,-i`}``



## 总结

本文参考了大量前人的文章，归根结底是因为 java.lang.Runtime#exec 中 StringTokenizer 会将空格进行分隔，导致原本命令执行的语义发生了变化，利用数组和编码可以成功执行命令。



## 参考文章

[Java下奇怪的命令执行](http://www.lmxspace.com/2019/10/08/Java%E4%B8%8B%E5%A5%87%E6%80%AA%E7%9A%84%E5%91%BD%E4%BB%A4%E6%89%A7%E8%A1%8C/)

[Java Runtime.getRuntime().exec由表及里](https://xz.aliyun.com/t/7046)

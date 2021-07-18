
# 【技术分享】实现基于时间的远程代码执行（RCE）技术（含工具下载）


                                阅读量   
                                **89984**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](./img/85644/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](./img/85644/t01058a7ea3f77930fa.jpg)](./img/85644/t01058a7ea3f77930fa.jpg)

****

翻译：[desword](http://bobao.360.cn/member/contribute?uid=2634189913)

预估稿费：170RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿

**<br>**

**0x1 前言**

本文主要介绍了作者在进行渗透测试项目的过程中，如何利用基于时间反馈的方式，突破无法获得命令输出反馈的限制，实现远程代码执行技术。

我们最近进行了一个渗透测试的项目，该项目的主要目的是测试目标主机某个API的漏洞以及可能造成的损害。该主机在一个被防火墙隔离的私有网络中，我们最终是利用基于时间的命令注入攻击完成的测试。

以下是整个渗透测试的心路历程。

首先，我们发现了一个有趣的GET请求，它接收了两个参数：一个是string类型，另一个是ID号。通过对string类型参数进行fuzzing测试，并基于它处理单引号的方式，我们发现它看起来是个SQL注入，然而普通的SQL注入攻击测试并没有成功。但是当我们发送`sleep 10`命令，并且HTTP响应确实在10秒后返回时，我们发现这里应当是个突破口，可以做一些文章。接下来，我们将设法攻击主机，以实现远程代码执行（RCE）。

第一个任务应当是识别目标主机运行在什么平台上。开始时，根据HTTP响应的头部，我们认为该主机是基于Windows平台的，然而测试结果却很奇怪，因为有的载荷应当只能在Linux的bash里面工作，在这个主机上却也能够工作。

为了确定该主机到底基于什么平台，我们的思路是：使用一个包含了sleep命令的“if”语句来识别到底是哪个系统。当条件为真是，sleep命令将被执行。

[![](./img/85644/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t018569fda38d678c2e.png)

为了能够执行得到上述sleep命令的结果，我们的第二个任务就是想办法与该主机进行交互。然而，实现交互也并不简单。我们尝试了许多工具用来建立TCP连接：ncat，wget，curl等。但没有一个可以成功。 然后，我们尝试了其他类似的技术：FTP连接，DNS查询，甚至ICMP数据包，但也没有成功。 再后来，我们才发现，这个主机处在一个私有网络中，保护该主机的防火墙允许我们执行命令，但是看不到输出。

我们项目的同事给出了一个建议，即使用sleep命令的返回结果去一个字符一个字符的猜命令执行的输出，当然，这个过程可以写个自动化脚本去完成。 这有点像执行基于时间的SQL注入一样。

 

[![](./img/85644/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t011be2c58bd82c6ca6.png)

那么，为了测试这种方式在有网络延迟的情况下是否有效，我们首先尝试了一个简单的脚本，它用来判断，在命令输出的结果中位置X的字符是否是Y。

通过上面这个脚本，我们可以得到whoami命令输出。

上面的方法看似可行，但是暴力枚举的猜测是一个十分低效的方式（事实上，作者后来也没解决这个问题= =）。除了这个问题以外，该方法还有其他严重的问题，比如，GET参数仅限于48个字符，因为不满足这个限制将会超过载荷的最大长度。为了绕过这个限制，我们的思路是将命令的输出分割，分割的部分分别存在目标主机的不同临时文件中。之后，我们再依次读取分割后的命令输出内容，那么，最终的输出结果就是所有内容的合并。

[![](./img/85644/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t011851abbd6b8928cf.png)

利用上述方式构造的载荷，我们可以控制GET参数为48个字符。令人沮丧的是，新的问题又出现了，我们执行的命令长度也有限制：最多9个字符长度。

为了解决这个问题，结合前面分割命令输出的方式，我们也将命令本身的内容分割，然后分别放到不同的脚本中，之后，再依次串连执行分割在不同脚本中的命令，就能够达到我们的效果，缩短命令的长度。（真是一件绣花针似的活）

综合以上所有内容，我们基于python制作了一个工具，它可以完成上述所有事情。

<br>

**0x2 为什么使用这个工具而不是现有的工具？**

有一个类似的工具 [commix](https://github.com/commixproject/commix)， [commix](https://github.com/commixproject/commix) 中有很多可用的渗透出技术，包括基于时间的渗透技术，它还可以识别目标主机操作系统类型，以及含有的命令注入漏洞。 虽然这是一个强大的工具，但是我们不选择使用 [commix](https://github.com/commixproject/commix)主要的原因有两个：

1、[commix](https://github.com/commixproject/commix)所使用的有效载荷 很长，在我们这里不适用。

2、其次，它很慢，会花费大量的时间来提取一个whoami命令输出。

<br>

**0x3 该工具如何工作？**

该工具有3个部分：

1. 用来猜测文件（length.py或length.bat）输出命令长度的脚本。

2. 用来猜测X位置字符的ASCII值（ascii.py或ascii.bat）的脚本。

3. 用来发送命令并分析响应时间，以判断条件输出的脚本。

提取过程主要两步：

1. 将命令输出写入文件

2. 使用length.py脚本猜测命令输出长度：

为了要猜测命令输出的长度，将按照如下格式：

```
python ascii.py {NUMBER} {IS_GREATER} {WHERE_THE_OUTPUT_IS_AT} {TIME_DELAY}
```

1.输出是否大于0？ ： python l.py 0 0 0 4 =&gt;无检测的延迟，这意味着它是真的

2. 比10大吗 ?: python l.py      10 0 0 4 =&gt; 4秒延时检测，这意味着这是假 的

3. 输出等于10？： python l.py      10 1 0 4 =&gt;没有检测到的延迟，这意味着是假的

4. 输出等于9？： python l.py      9 1 0 4 =&gt; 4秒延时检测，这意味着我们找到了输出长度

在我们知道输出长度之后，我们现在可以继续猜测ASCII字符代码。 这个任务是由ascii.py完成： 

```
python ascii.py {CHAR_POS} {ASCII_VALUE} {IS_GREATER} {WHERE_THE_OUTPUT_IS_AT} {TIME_DELAY}.
```

猜测过程与猜测命令输出的长度相同。我们用猜测一个特定字符的ASCII值来代替猜测长度。

这里是本工具的一些输出结果： <br>

[![](./img/85644/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01ef5600a009863070.png)

提取uname -a：

[![](./img/85644/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t017475cbf6de01d4f6.png)

[![](./img/85644/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01c708f0b1fc92bbbd.png)

我们进一步尝试提取/etc/password的长度约2863，它能够正常工作： 

[![](./img/85644/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01cf3952b698e485ac.png)

为了测试效果，您可以使用以下简单的PHP脚本：

[![](./img/85644/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t019aecc760c437b93e.png)

该工具可从这里下载：

[https://github.com/dancezarp/TBDEx](https://translate.google.com/translate?hl=zh-CN&amp;prev=_t&amp;sl=en&amp;tl=zh-CN&amp;u=https://github.com/dancezarp/TBDEx)

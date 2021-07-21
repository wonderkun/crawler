> 原文链接: https://www.anquanke.com//post/id/189316 


# 使用 Ghidra 分析 phpStudy 后门


                                阅读量   
                                **675679**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p4.ssl.qhimg.com/t0157837986bd7b9434.jpg)](https://p4.ssl.qhimg.com/t0157837986bd7b9434.jpg)



作者：lu4nx@知道创宇404积极防御实验室

作者博客：[《使用 Ghidra 分析 phpStudy 后门》](https://www.shellcodes.org/Hacking/%E4%BD%BF%E7%94%A8Ghidra%E5%88%86%E6%9E%90phpStudy%E5%90%8E%E9%97%A8.html)



这次事件已过去数日，该响应的也都响应了，虽然网上有很多厂商及组织发表了分析文章，但记载分析过程的不多，我只是想正儿八经用 Ghidra 从头到尾分析下。



## 1 工具和平台

主要工具：
- Kali Linux
- Ghidra 9.0.4
- 010Editor 9.0.2
样本环境：
- Windows7
- phpStudy 20180211
## 2 分析过程

先在 Windows 7 虚拟机中安装 PhpStudy 20180211，然后把安装完后的目录拷贝到 Kali Linux 中。

根据网上公开的信息：后门存在于 php_xmlrpc.dll 文件中，里面存在“eval”关键字，文件 MD5 为 c339482fd2b233fb0a555b629c0ea5d5。

因此，先去找到有后门的文件：

将文件 ./PHPTutorial/php/php-5.4.45/ext/php_xmlrpc.dll 单独拷贝出来，再确认下是否存在后门：

从上面的搜索结果可以看到文件中存在三个“eval”关键字，现在用 Ghidra 载入分析。

在 Ghidra 中搜索下：菜单栏“Search” &gt; “For Strings”，弹出的菜单按“Search”，然后在结果过滤窗口中过滤“eval”字符串，如图：

[![](https://p0.ssl.qhimg.com/t01431c0510670c4172.png)](https://p0.ssl.qhimg.com/t01431c0510670c4172.png)

从上方结果“Code”字段看的出这三个关键字都位于文件 Data 段中。随便选中一个（我选的“@eval(%s(‘%s’));”）并双击，跳转到地址中，然后查看哪些地方引用过这个字符串（右击，References &gt; Show References to Address），操作如图：

[![](https://p3.ssl.qhimg.com/t0153e4a89eef531cd9.png)](https://p3.ssl.qhimg.com/t0153e4a89eef531cd9.png)

结果如下：

[![](https://p2.ssl.qhimg.com/t01713b3a36ef62f522.png)](https://p2.ssl.qhimg.com/t01713b3a36ef62f522.png)

可看到这段数据在 PUSH 指令中被使用，应该是函数调用，双击跳转到汇编指令处，然后 Ghidra 会自动把汇编代码转成较高级的伪代码并呈现在 Decompile 窗口中：

[![](https://p4.ssl.qhimg.com/t018b8b4e3dd20bce6a.png)](https://p4.ssl.qhimg.com/t018b8b4e3dd20bce6a.png)

如果没有看到 Decompile 窗口，在菜单Window &gt; Decompile 中打开。

在翻译后的函数 FUN_100031f0 中，我找到了前面搜索到的三个 eval 字符，说明这个函数中可能存在多个后门（当然经过完整分析后存在三个后门）。

这里插一句，Ghidra 转换高级代码能力比 IDA 的 Hex-Rays Decompiler 插件要差一些，比如 Ghidra 转换的这段代码：

在IDA中翻译得就很直观：

还有对多个逻辑的判断，IDA 翻译出来是：

Ghidra 翻译出来却是：

而多层 if 嵌套阅读起来会经常迷路。总之 Ghidra 翻译的代码只有反复阅读后才知道是干嘛的，在理解这类代码上我花了好几个小时。

### 2.1 第一个远程代码执行的后门

第一个后门存在于这段代码：

阅读起来非常复杂，大概逻辑就是通过 PHP 的 zend_hash_find 函数寻找 $_SERVER 变量，然后找到 Accept-Encoding 和 Accept-Charset 两个 HTTP 请求头，如果 Accept-Encoding 的值为 gzip,deflate，就调用 zend_eval_string 去执行 Accept-Encoding 的内容：

这里 zend_eval_string 执行的是 local_10 变量的内容，local_10 是通过调用一个函数赋值的：

函数 FUN_100040b0 最后分析出来是做 Base64 解码的。

到这里，就知道该如何构造 Payload 了：

朝虚拟机构造一个请求：

结果如图：

[![](https://p3.ssl.qhimg.com/t013601a5cf43b048b3.png)](https://p3.ssl.qhimg.com/t013601a5cf43b048b3.png)

### 2.2 第二处后门

沿着伪代码继续分析，看到这一段代码：

重点在这段：

变量 puVar8 是作为累计变量，这段代码像是拷贝地址 0x1000d66c 至 0x1000e5c4 之间的数据，于是选中切这行代码：

双击 DAT_1000d66c，Ghidra 会自动跳转到该地址，然后在菜单选择 Window &gt; Bytes 来打开十六进制窗口，现已处于地址 0x1000d66c，接下来要做的就是把 0x1000d66c~0x1000e5c4 之间的数据拷贝出来：
1. 选择菜单 Select &gt; Bytes；
1. 弹出的窗口中勾选“To Address”，然后在右侧的“Ending Address”中填入 0x1000e5c4，如图：
[![](https://p5.ssl.qhimg.com/t018f9959b9c87b4a5f.png)](https://p5.ssl.qhimg.com/t018f9959b9c87b4a5f.png)

按回车后，这段数据已被选中，我把它们单独拷出来，点击右键，选择 Copy Special &gt; Byte String (No Spaces)，如图：

[![](https://p2.ssl.qhimg.com/t01222a3541091f9e50.png)](https://p2.ssl.qhimg.com/t01222a3541091f9e50.png)

然后打开 010Editor 编辑器：
1. 新建文件：File &gt; New &gt; New Hex File；
1. 粘贴拷贝的十六进制数据：Edit &gt; Paste From &gt; Paste from Hex Text
然后，把“00”字节全部去掉，选择 Search &gt; Replace，查找 00，Replace 那里不填，点“Replace All”，处理后如下：

[![](https://p2.ssl.qhimg.com/t013fc1a550859b0c47.png)](https://p2.ssl.qhimg.com/t013fc1a550859b0c47.png)

把处理后的文件保存为 p1。通过 file 命令得知文件 p1 为 Zlib 压缩后的数据：

用 Python 的 zlib 库就可以解压，解压代码如下：

执行结果如下：

用 base64 命令把这段 Base64 代码解密，过程及结果如下：

### 2.3 第三个后门

第三个后门和第二个实现逻辑其实差不多，代码如下：

重点在这段：

后门代码在地址 0x1000d028~0x1000d66c 中，提取和处理方法与第二个后门的一样。找到并提出来，如下：

把这段Base64代码解码：



## 3 参考
- [https://github.com/jas502n/PHPStudy-Backdoor](https://github.com/jas502n/PHPStudy-Backdoor)
- 《phpStudy 遭黑客入侵植入后门事件披露 | 微步在线报告》
- [《PhpStudy 后门分析》，作者：Hcamael@知道创宇 404 实验室](https://paper.seebug.org/1044/)
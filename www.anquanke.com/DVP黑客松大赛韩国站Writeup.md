> 原文链接: https://www.anquanke.com//post/id/189724 


# DVP黑客松大赛韩国站Writeup


                                阅读量   
                                **828399**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p2.ssl.qhimg.com/t01372a98782fbece99.jpg)](https://p2.ssl.qhimg.com/t01372a98782fbece99.jpg)



本部分由长亭科技区块链安全负责人于晓航撰写

## Writeup 1: Monica’s Bank

### <a class="reference-link" name="0x00%20%E6%A6%82%E5%86%B5"></a>0x00 概况

这题是几种Solidity常见经典漏洞的组合，如果对Solidity熟悉的话会相对简单。

### <a class="reference-link" name="0x01%20%E6%80%9D%E8%B7%AF"></a>0x01 思路

在transferBalance函数里，由于整数溢出require并没啥用，只需要随意transfer任意小余额到其他地址就可以获得大量balance。

然后可以buy 1个credit，这里的随机数是完全可预测的，只需要把随机数那段代码复制到攻击合约里就好了。

最后一步是重入攻击，跟hint里说的一样，这个类似DAO的加强版攻击。大概意思是只需要重入1次就好，而不是多次重入，这样可以触发creditOf[] -= amount的整数溢出。

在DAO攻击中，目标函数和攻击合约的fallback都被调用了很多次，直到gas耗尽，调用链底层抛出异常，由于.call.value特点是返回false而非继续向上抛出异常，所以这整个交易不会被revert，然后.call.value之后的代码们只会被执行1次。

在‘加强版’攻击里，由于我们主动结束第二次fallback，.call.value之后的代码会被执行2次，从而触发整数下溢，达成目标。

### <a class="reference-link" name="0x02%20%E8%A7%A3%E5%AF%86Flag"></a>0x02 解密Flag

触发SendFlag后，后台脚本会把加密flag数据放在交易里发送给攻击者的地址，即tx.origin。

数据是用tx.origin的公钥加密的，因此可以用私钥，和提供的解密脚本来解密。

### <a class="reference-link" name="0x03%20POC"></a>0x03 POC

[![](https://p1.ssl.qhimg.com/t01d370dbc84c6d0156.png)](https://p1.ssl.qhimg.com/t01d370dbc84c6d0156.png)

### <a class="reference-link" name="0x04%20%E5%BD%A9%E8%9B%8B"></a>0x04 彩蛋

[![](https://p3.ssl.qhimg.com/t01e242f292072435df.png)](https://p3.ssl.qhimg.com/t01e242f292072435df.png)



## Writeup 2: Monica’s Casino

### <a class="reference-link" name="0x00%20%E6%A6%82%E5%86%B5"></a>0x00 概况

这题属于中等偏难，是个EVM JOP类型蜜罐合约题目。需要逆向合约opcode，找一些gadgets来准备好栈以及操作控制流，利用后门。

### <a class="reference-link" name="0x01%20JOP%E6%80%9D%E8%B7%AF"></a>0x01 JOP思路

Constructor里有jump指令，跳到参数a，通过分析合约创建交易的input data可以知道是0x9b。

在remix里调试一下可以看到0x9b指向的是参数b的开头，刚好这里有一个jumpdest字节码所以程序可以合法跳到这里，执行后面的指令。b开头这段指令做的事很简单：将b的后半段字节copy到memory上，然后直接return这些字节。所以这一步其实就是替换掉了合约在链上的runtime code，所以runtime code其实跟源码看到的不一样。

严格来说现在runtimecode可以是任意内容，这样的话会需要很多比较无聊的逆向工作，但这里可以尝试的一个技巧是，把源码里constructor的jump一行注释掉，然后编译得到原本的runtime code，然后比较这两个版本。会发现这里我在‘有效字节码部分’只patch了1个字节。

[![](https://p4.ssl.qhimg.com/t0194d46cca096ccbd2.png)](https://p4.ssl.qhimg.com/t0194d46cca096ccbd2.png)

如上，第一处diff是1字节，第二处是metadata，这个理论上来说对不同源码是应该不一样的（但这里是题目有意设置的不同）。

第一个字节把push32(0x7f)改成了dup3(0x82)，实际上把后面的字节从‘数据段’解放为了‘代码段’。然后其实后续的这些字节就是源码中salt的值。

于是这部分字节可以被解释为这段opcode：

[![](https://p2.ssl.qhimg.com/t01dc2b03cef394aa35.png)](https://p2.ssl.qhimg.com/t01dc2b03cef394aa35.png)

这里可以看到有了第一个任意跳转，也就是后门的入口，然后还有挺多事要做。通过msg.sender[msg.sender[-1]]这个字节可以控制地址。

接下来目标是控制合约触发event，即log字节码，也就是需要跳到log前的某个jumpdest。

从这里可能会有人尝试直接一步到位跳到log，但其实会发现那个地方的地址要高于0xff没法通过1字节控制。

因此我们需要跳转到小于0x100的某个位置，总之最后落在salt的后半段，然后再通过inputdata的其他字节控制跳转到下一个gadget。

可能会注意到的另一个事情是在最近的‘jumpdest’和‘log’之间，存在一些修改栈内容的操作，因此我们需要利用其他gadgets大概准备一下stack的内容。

接下来的步骤是需要跳转到metadata段来处理一些stack/memory的存取操作（正常情况下metadata段不会被执行）

Ummm，我觉得写到这里差不多，还是希望把其他乐趣留给大家来探索接下来的解法。后面的解题应该还会有几个trick没有提到。

### <a class="reference-link" name="0x02%20%E6%9C%AA%E5%88%9D%E5%A7%8B%E5%8C%96%E7%BB%93%E6%9E%84%E4%BD%93%E5%8F%98%E9%87%8F"></a>0x02 未初始化结构体变量

在走到后门入口之前有另一个trick需要处理一下。未初始化结构体变量也是一个很典型的蜜罐合约，在旧版编译器下，‘PlayerInfo pi’这种写法其实定义了一个指向0的指针，刚好也是secret存储的位置，因此pi.addr = msg.sender其实悄悄把secret修改成了msg.sender。

所以lottery函数的参数应该是攻击者自己的地址。这个设计像是后门的守卫。总之这样我们就可以触发到后门了。

另一个点是，由于我们需要给lottery提供的inputdata要长于uint256来触发JOP部分，可能需要用web3脚本或者部署一个代理合约来构造发送任意payload。然后为了减轻选手的压力，我写了一个docker image作为完整的独立debug环境，作为题目附件可供下载，启动后里面有一个包含题目环境的私链，与ropsten上的环境几乎一模一样，也提供了几乎所有解题需要用到的库、脚本样例啥的。

### <a class="reference-link" name="0x03%20POC"></a>0x03 POC

[![](https://p1.ssl.qhimg.com/t01599d02034a00c484.png)](https://p1.ssl.qhimg.com/t01599d02034a00c484.png)

如果你有debug环境的话直接run docker，记得暴露一下rpc/ws接口，然后把remix连到docker里的私链来debug。如果没有的话用ropsten也是一样的。

接下来配置一下ws_provider跑poc就完事儿了，应该会发一条交易触发SendFlag。可以尝试debug poc这条交易来理解一些细节。

关于如何解密flagdata，请参考‘Monica’s Bank Writeups’。

感谢，希望大家喜欢这小破题。

完事儿

FYI: [http://xhyumiracle.com/defcon27-village-talk/](http://xhyumiracle.com/defcon27-village-talk/)



本部分由白帽汇高级安全研究专员R3start撰写

## Writeup 1: Controllable Database Connection

打开网站提示“Please connect to the database first” 还有一个 Connect的链接 所以应该跟数据库有关

[![](https://p2.ssl.qhimg.com/t016299f50492295b94.png)](https://p2.ssl.qhimg.com/t016299f50492295b94.png)

点击链接后发现URI 多了/#mysql.php 看来是个提示

[![](https://p2.ssl.qhimg.com/t014355103848aa6c69.png)](https://p2.ssl.qhimg.com/t014355103848aa6c69.png)

访问mysql.php 提示 Error 常规套路扫一波源码

[![](https://p1.ssl.qhimg.com/t014cb95e32c2d90e67.png)](https://p1.ssl.qhimg.com/t014cb95e32c2d90e67.png)

得到备份文件 /mysql.php.bak 获取到源码

[![](https://p5.ssl.qhimg.com/t016337c24b56c87b58.png)](https://p5.ssl.qhimg.com/t016337c24b56c87b58.png)

发现连接地址、用户名、密码参数可控，看来考点是mysql伪造恶意服务端读取客户端文件，按照泄露的源码来看，应该是要读 /Flag.php 文件

[![](https://p3.ssl.qhimg.com/t011ab9602b4363f366.png)](https://p3.ssl.qhimg.com/t011ab9602b4363f366.png)

通过连接自己公网开启的恶意mysql服务端读取成功读取到Flag.php 的源码

[![](https://p0.ssl.qhimg.com/t0164f3008190b498dd.png)](https://p0.ssl.qhimg.com/t0164f3008190b498dd.png)

Flag.php 是一个简单命令执行绕过，限制使用eval、assert函数和长度不得超过11位，满足以上两个条件进入eval函数执行

[![](https://p0.ssl.qhimg.com/t016fac2616fae95c85.png)](https://p0.ssl.qhimg.com/t016fac2616fae95c85.png)

我们可以使用反单引号执行命令，并通过$_GET传入我们需要执行的命令，长度刚好11个字符内

[![](https://p3.ssl.qhimg.com/t0124f3706df040f768.png)](https://p3.ssl.qhimg.com/t0124f3706df040f768.png)

成功反弹shell 并获取到Flag

[![](https://p0.ssl.qhimg.com/t01f37a1708cbf70562.png)](https://p0.ssl.qhimg.com/t01f37a1708cbf70562.png)



## Writeup 2: Unsafe Access

打开网站只有一张logo和一个提示 6_79？很自然的就想到应该跟6379，redis有关!

[![](https://p1.ssl.qhimg.com/t01a41dc680c2bd3cb4.png)](https://p1.ssl.qhimg.com/t01a41dc680c2bd3cb4.png)

右键查看源码发现一个被注释的链接

[![](https://p4.ssl.qhimg.com/t01373180d69a696b3f.png)](https://p4.ssl.qhimg.com/t01373180d69a696b3f.png)

测试发现此接口存在SSRF漏洞

[![](https://p4.ssl.qhimg.com/t01efcc7897c356105f.png)](https://p4.ssl.qhimg.com/t01efcc7897c356105f.png)

扫描备份文件获取到link.php的源码，只是简单的进行了一些过滤，限制了gopher和127、localhost 等字符

[![](https://p3.ssl.qhimg.com/t0123158d245838720d.png)](https://p3.ssl.qhimg.com/t0123158d245838720d.png)

联系首页的6_79提示，看来这题是常规的SSRF配合Redis拿Flag。使用dict协议写入redis、使用0 代表当前IP或域名解析等方式即可绕过访问本地限制。尝试反弹或者写私钥，均没有成功应该是权限过低的原因，于是尝试写webshell，成功写入恶意代码，获取到Flag。

写入恶意代码：（&lt;? 等特殊符号需要转义，不然问号后面会导致截断无法写入）

[![](https://p0.ssl.qhimg.com/t01702c3267334168cd.png)](https://p0.ssl.qhimg.com/t01702c3267334168cd.png)<br>
设置保存路径：

[![](https://p2.ssl.qhimg.com/t0144a9f5e642ecd66c.png)](https://p2.ssl.qhimg.com/t0144a9f5e642ecd66c.png)<br>
设置保存名字：

[![](https://p0.ssl.qhimg.com/t015568703eb5791b2d.png)](https://p0.ssl.qhimg.com/t015568703eb5791b2d.png)<br>
保存：

[![](https://p1.ssl.qhimg.com/t016941f4e581e2eaa1.png)](https://p1.ssl.qhimg.com/t016941f4e581e2eaa1.png)

成功写入

[![](https://p4.ssl.qhimg.com/t01f342007f565cf4b0.png)](https://p4.ssl.qhimg.com/t01f342007f565cf4b0.png)



本部分由PeckShield漏洞研究总监Edward Lo撰写

## Remote DoS

这是公链项目的第一题，参赛者需要找到漏洞并进行攻击造成Remote DoS。服务器上跑的是经过修改的geth结点，而问题点就在EVM中。

首先来看看EVM正常执行流程：

[![](https://p4.ssl.qhimg.com/t01682dd4b2b52203d1.png)](https://p4.ssl.qhimg.com/t01682dd4b2b52203d1.png)

EVM在执行合约时，会一步一步提取其中的OPCode，并做相对应的检查：

OPCode需要的传参是否已放到栈(stack)上，是否有足够空间能放回传值;

EVM目前是否在readonly模式(例如以static_call方式呼叫)，若是则需符合规则，不能对链上状态有任何改动(例如转帐);

[![](https://p1.ssl.qhimg.com/t01a449200cee064d9c.png)](https://p1.ssl.qhimg.com/t01a449200cee064d9c.png)

计算OPCode需要的内存大小，并根据目前的内存情况决定如何收取gas费用并扩容内存。

接下来我们以OPCode mstore8为例，来看看到底怎麽计算。

[![](https://p2.ssl.qhimg.com/t0123f948fe9db1ae0d.png)](https://p2.ssl.qhimg.com/t0123f948fe9db1ae0d.png)

如上所示，p是offset，v是想写入的内容

[![](https://p0.ssl.qhimg.com/t0127e116087ad2d045.png)](https://p0.ssl.qhimg.com/t0127e116087ad2d045.png)

EVM会调用memoryMStore8计算回传所需要的内存大小，接着调用gasMStore8来计算所需的gas费用

[![](https://p2.ssl.qhimg.com/t01eacf45ffbc786f15.png)](https://p2.ssl.qhimg.com/t01eacf45ffbc786f15.png)

这道题目就是将memoryMStore8注解掉，如此一来会造成两个问题:

EVM不会计算收取gas，因为memorySize永远为0;

内存不会扩容，攻击者可以在任意offset写入一个可控byte内容;

如此一来，只需布置会调用mstore8的恶意合约便可以进行攻击

[![](https://p3.ssl.qhimg.com/t01b9eb4bddf810de61.png)](https://p3.ssl.qhimg.com/t01b9eb4bddf810de61.png)



## RCE

基于上一道题目，我们可以在任意offset写一个byte，理论上便能透过它执行RCE。此题的技术难度跟水平要求较高，攻击者必须结合漏洞并布置巧妙构思过的恶意合约，将shellcode写入远端节点来完成RCE

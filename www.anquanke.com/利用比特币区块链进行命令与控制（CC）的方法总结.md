
# 利用比特币区块链进行命令与控制（CC）的方法总结


                                阅读量   
                                **778791**
                            
                        |
                        
                                                                                    



[![](./img/199465/t0127763d51a53f1289.jpg)](./img/199465/t0127763d51a53f1289.jpg)



由于区块链具备不易封锁、不易篡改、不易溯源、易于访问等特点，一些业界人士提出了使用区块链进行CC的方法。就目前的调研情况来看，可根据载体的不同，将这些利用方法分为两类：一类是以比特币的交易为载体进行CC，另一类是以区块链的其他应用（如以太坊）为载体进行CC。本次报告主要介绍以比特币的交易为载体进行CC的方法。<br>
根据利用方式的不同，可以将以比特币交易为载体的CC方法分以下几种。

<th style="text-align: center;">载体</th><th style="text-align: left;">原理</th><th style="text-align: left;">局限</th>
|------
<td style="text-align: center;">交易脚本</td><td style="text-align: left;">OP_RETURN类型的脚本可以输入83字节的自定义内容</td><td style="text-align: left;">UTXO需要比特币消耗</td>
<td style="text-align: center;">交易值</td><td style="text-align: left;">使用交易的数字隐藏信息</td><td style="text-align: left;">可利用长度受限,存在被外界干扰的风险</td>
<td style="text-align: center;">数字签名</td><td style="text-align: left;">命令编码到私钥中,利用ECDSA临时密钥重用恢复私钥</td><td style="text-align: left;">泄露私钥</td>
<td style="text-align: center;">数字签名</td><td style="text-align: left;">命令编码到随机数中,利用ECDSA随机密钥重用恢复私钥，进行验证</td><td style="text-align: left;">Bot端计算量大</td>
<td style="text-align: center;">数字签名</td><td style="text-align: left;">利用不同的随机数,把命令编码到签名值中</td><td style="text-align: left;">计算量较大,命令长度受限</td>

本文将按照下述思路进行介绍：首先对比特币交易的字段进行介绍，包括交易的组成和字段含义；随后介绍以交易脚本和交易值进行CC的方法；接下来对椭圆曲线密码算法进行介绍；然后介绍利用ECDSA进行CC的方法。



## 概念

### <a class="reference-link" name="%E4%BA%A4%E6%98%93"></a>交易

交易是比特币系统中的重要组成部分。通过交易，比特币的所属权发生转换。比特币中的节点验证每个交易，并将通过验证的交易写入区块中。交易包含输入输出信息和验证信息，其本质是一个数据结构。交易的结构如下。

[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t011a9a9dfaf88079c9.png)

### <a class="reference-link" name="UTXO"></a>UTXO

UTXO（Unspent Transaction Output，未使用的交易输出）是比特币交易的基本单位。UTXO是交易中未被使用的输出。比特币中的节点会维护一个记录所有UTXO的清单。交易的实质是将一部分UTXO转换为另一部分UTXO。经过确认后，交易的输出是新产生的UTXO，它记录着比特币数额和地址。当要使用这部分比特币时，需要创建新的交易。新交易的输入为UTXO，它指向了该UTXO的“地址”（生成该UTXO的交易哈希及输出中的顺序）。当新的交易被确认后，将产生新的UTXO，旧的UTXO不再存在。

下图是一个比特币交易。这笔交易中有两个输入和两个输出。在交易发出时，这两个输入是两个UTXO，分别对应着不同的比特币地址和比特币数量；输出是将要形成的两个UTXO，对应着不同的比特币地址和数量。当交易经过确认加入区块链上之后，这两个输入由Unspent状态变为Spent状态，不再是UTXO；这两个输出形成两个新的UTXO。若比特币地址3PbJsixkjmjzsjCpi4xAYxxaL5NnxrbF9B的拥有者要使用这笔比特币，需要将这个UTXO作为下一个交易的输入，并提供身份验证信息。待该交易得到确认时，这个输入将标记为Spent状态，不再是UTXO。

[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01efba7487809b0be0.png)

**图为交易556a0660944f18fad91492eee67678479f936a666f74717a0fecf0b738f7a791。两个输出中，标记为橙色的为Spent状态，已被使用；标记为绿色的为Unspent状态，是一个UTXO。**

UTXO不可再分，UTXO中的比特币数量在下一次交易时将全部使用。UTXO中比特币数量的单位为中本聪（Satoshi），1 BTC = 10 000 000 sat，1 sat=0.00000001 BTC。若一个UTXO的比特币数量不足，可以输入多个UTXO。当输入的比特币总数量大于输出目标需要的数量时，可以在输出中设置“找零”。接收“找零”的比特币地址可以与输入的比特币地址相同，也可以不同。每一笔交易输入的比特币数量都要略大于输出的比特币数量，多出的这部分将作为手续费奖励给矿工。手续费越高，该笔交易被确认的速度越快。若交易中没有设置“找零”，则多出来的比特币数量默认为该笔交易的手续费。例如，下图的交易中共有4个输入，输入的比特币总额为0.04320707 BTC；输出有两个，输出的比特币总额为0.04186037 BTC；剩余的0.00134670 BTC为这笔交易的手续费。

[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0120e2ebb74e45dcd1.png)

**图为交易ce31dfaa0fd6f0a80728fc776de795ba30494dbd72b4834dd4613fe7529ab914**

### <a class="reference-link" name="%E8%84%9A%E6%9C%AC"></a>脚本

一个交易需要满足以下条件才能被比特币节点当作一个合法的交易写入区块链上：

（1）输入均为UTXO。<br>
（2）输入的比特币总数大于输出的比特币总数。<br>
（3）能完成对输入的身份验证。

完成对输入的身份验证需要使用交易脚本。交易脚本类似于Forth语言，基于栈，并由左向右执行。脚本是一系列记录在交易里的指令，描述了下一个要使用比特币的人应以何种方式获取相应的权限。只有当交易中的输入能满足上一个交易中的输出里设定的条件后，交易才能继续。交易输出里的脚本为锁定脚本（scriptPubKey），设置了要使用这笔比特币需要满足的条件。交易输入含有解锁脚本（scriptSig），用于和对应的锁定脚本匹配，证明使用者拥有比特币的使用权。

在验证交易时，需要将解锁脚本和锁定脚本放在一起执行，执行的过程需要将把连起来的脚本按从左到右的顺序依次执行对应的命令。脚本的命令又称为Opcodes、关键字、功能等，包括常量类、控制流类、堆栈类、位运算类、数字运算类、密码运算类等共10个类别，可以通过一系列运算完成对交易的身份验证。交易脚本共有5种类型，分别为P2PKH（Pay-to-Public-Key-Hash）、P2PK（Pay-to-Public-Key）、多重签名（Multiple Signatures，MS）、P2SH（Pay-to-Script-Hash）和数据输出（OP_RETURN），每种类型的锁定脚本和解锁脚本有着不同的格式，如下表。其中在比特币交易中最常见的是P2PKH类型。

|类型|名称|scriptSig|scriptPubKey
|------
|P2PKH|Pay-to-Public-Key-Hash|&lt;sig&gt;&lt;pubKey&gt;|OP_DUP OP_HASH160 &lt;pubKeyHash&gt; OP_EQUALVERIFY OP_CHECKSIG
|P2PK|Pay-to-Public-Key|&lt;sig&gt;|&lt;pubKey&gt; OP_CHECKSIG
|多重签名|Multiple Signatures|OP_0 &lt;sigA&gt; &lt;sigB&gt; … &lt;sigM&gt;|M &lt;pubKey1&gt; &lt;pubKey2&gt; … &lt;pubKeyN&gt; N OP_CHECKMULTISIG
|P2SH|Pay-to-Script-Hash|&lt;sig&gt; &lt;script&gt;|OP_HASH160 &lt;scriptHash&gt; &lt;OP_EQUAL&gt;
|数据输出|OP_RETURN|–|OP_RETURN {zero or more ops}

下表是以P2PKH为例的交易脚本执行过程。第一列代表命令执行时堆栈的情况，第二列代表命令的从左到右执行。比特币官方WiKi网站（[https://en.bitcoin.it/wiki/Script）](https://en.bitcoin.it/wiki/Script%EF%BC%89) 对脚本中的命令及对应的代码进行了说明。在命令执行中，节点能通过对公钥和签名的校验，完成对使用者的身份验证。只有持有相应地址的私钥，才能生成正确的签名。

|堆栈|脚本|描述
|------
||&lt;**sig**&gt; &lt;**pubKey**&gt; OP_DUP OP_HASH160 &lt;pubKeyHash&gt; OP_EQUALVERIFY OP_CHECKSIG|连接scriptSig和scriptPubKey
|&lt;pubKey&gt; &lt;sig&gt;|**OP_DUP** OP_HASH160 &lt;pubKeyHash&gt; OP_EQUALVERIFY OP_CHECKSIG|常量入栈
|&lt;pubKey&gt;&lt;pubKey&gt;&lt;sig&gt;|**OP_HASH160** &lt;pubKeyHash&gt; OP_EQUALVERIFY OP_CHECKSIG|复制栈顶元素
|&lt;pubHashA&gt;&lt;pubKey&gt;&lt;sig&gt;|&lt;**pubKeyHash**&gt; OP_EQUALVERIFY OP_CHECKSIG|对栈顶元素求哈希
|&lt;pubKeyHash&gt;&lt;pubHashA&gt;&lt;pubKey&gt;&lt;sig&gt;|**OP_EQUALVERIFY** OP_CHECKSIG|常量入栈
|&lt;pubKey&gt;&lt;sig&gt;|**OP_CHECKSIG**|验证栈顶两个元素是否相同
|TRUE||校验栈顶两个元素的签名

由于区块链在其他领域具有很多潜在应用，许多开发者希望充分发挥区块链的优势。然而，如果在区块链上存储与交易无关的数据，会增加各节点的存储负担。经过比特币社区的讨论，最终从比特币0.9版本开始，在交易脚本里增加OP_RETURN类型，可以存储40字节的数据。从比特币0.12版本开始，OP_RETURN后最多可以添加83字节的数据。因OP_RETURN类型的交易无法指明比特币接收者地址，无法使用解锁脚本进行验证，因此每个OP_RETURN类型的交易都是一个UTXO，而且永远无法被使用。下图是一个使用OP_RETURN类型的交易存储数据的案例。交易者在OP_RETURN后面写入了一个十六进制字符串，该字符串经ASCII解码后为“Yuki will you marry me ? Tetsu.”。另一个OP_RETURN类型的交易进行了回复，其数据解码后为“Yes I will. Yuki.”。

[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01325d1a13c3ba9a6d.png)

**交易b17a027a8f7ae0db4ddbaa58927d0f254e97fce63b7e57e8e50957d3dad2e66e**

[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0195da49bb11b7a284.png)

**交易e89e09ac184e1a175ce748775b3e63686cb1e5fe948365236aac3b3aef3fedd0**<br>
增加OP_RETURN类型给区块链在其他领域的应用带来了便利之处，但也因此增加了区块链服务滥用的风险。



## 利用交易进行CC

### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E4%BA%A4%E6%98%93%E8%84%9A%E6%9C%AC%E8%BF%9B%E8%A1%8CCC"></a>利用交易脚本进行CC

OP_RETURN字段能够存储一定大小的数据，因此可以创建一个OP_RETURN类型的交易，把CC命令编码嵌入到OP_RETRUN字段中，发布交易，由写入了Bot master比特币地址的Bot进行检索、解码和执行。由于未被比特币节点确认的交易也能被检索到，故这里不用等待比特币节点进行交易确认的延时。

2014年，Syed Taha Ali等人基于此原理提出僵尸网络模型ZombieCoin。由于OP_RETURN字段能嵌入的数据大小有限，在此文中，作者提出了使用哈夫曼树对命令进行编码来节省字节数的方法。在验证性测试中，Bot运行在比特币0.9.0版本上，共包含5个命令，如下表。

|命令|参数|含义
|------
|PING|&lt;1&gt; &lt;website&gt; &lt;number&gt;|Ping指定网站指定次数
|REGISTER|&lt;2&gt; &lt;website address&gt;|Bot到指定网站注册
|LEASE|&lt;3&gt; &lt;block height&gt; &lt;BTC address&gt;|将Bot租给其他人
|DOWNLOAD DATA|&lt;4&gt; &lt;transactions&gt;|从指定的交易处下载数据
|SCREENSHOT|&lt;5&gt; &lt;server address&gt; &lt;number&gt;|把指定数量的截屏传到指定地址

在运行时，Bot相当于一个简化付款验证（Simplified Payment Verification，SPV）模式的比特币节点。相比于完整的比特币节点，这种模式的节点占用更少量的内存和存储。作者基于BitcoinJ库开发的Bot程序大小为7MB，在本地维护的区块链内容大小为626KB，其网络流量和其他SPV客户端的流量一致。

[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0136fd63a245d900a9.png)

为了测试不同地区的Bot性能，作者在实验室运行两个Bot，使用微软Azure云平台运行多个Bot，模拟了Bot在美国、巴西、欧洲、东亚等地区的运行情况。每个Bot单独连接到比特币网络，下载节点列表，寻找Bot master的交易。作者每隔1小时按上表的顺序下发一次命令，循环运行24小时，共收集2300个Bot的响应数据。整体来看（如上图），Bot能在命令发出5秒内做出响应的情况约占50%；在10秒内响应的情况约占90%；响应时间的中位数为5.54秒。

作者于2018年对ZombieCoin进行了完善，提出了ZombieCoin 2.0。作者实验时，比特币版本已经更新到0.11.0，OP_RETURN字段后可以添加80字节的数据。在ZombieCoin 2.0中，作者提出通过使用公共服务和DGA等解决Bot的数据回传问题。作者提出了让Bot使用Bot master的公钥加密载荷，把数据传到公共网络中。只有拥有对应私钥的Bot master才能解开数据。当指令过长时，可以通过把指令拆分到多个交易中进行分发。

这些方法均未彻底解决Bot数据回传的问题。使用区块链下发回连服务器地址、通过公共服务上传数据会在整个过程中引入不安全因素。ZombieCoin 2.0中提出使用Bot master的公钥对数据进行加密的方法。由于公钥加密数据效率过低，这种方法只在加密数据较少时适用，不适用于需要Bot进行大量数据回传的场景。另外，这些方法也没有解决流量异常的问题。在ZombieCoin中，作为SPV节点，Bot端会有大量的P2P流量，是一个明显的异常。这给Bot的隐蔽性带来了挑战。此外，由于OP_RETURN中存储着各种自定义的数据，此类型的交易会很容易被监视，例如CoinSecret（[http://coinsecrets.org/）](http://coinsecrets.org/%EF%BC%89) 就是一个专门用来记录OP_REETURN字段数据的网站。而在区块链上发布过多的OP_RETURN交易会引起异常，可能导致Bot master地址被禁用，会为CC带来一定的复杂性。

由于上述缺陷，在实际的CC中，往往会结合其他方法一起运用。2019年9月，TrendMicro的研究人员发现一种针对Windows用户的dropper Glupteba。该dropper使用OP_RETURN字段传递CC服务器地址。OP_RETURN字段后是AES加密的数据，前12字节为AES GCM标签，后32字节为AES密文，密钥被硬编码在二进制文件中。

### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E4%BA%A4%E6%98%93%E5%80%BC%E8%BF%9B%E8%A1%8CCC"></a>利用交易值进行CC

在交易中，另一个容易被定制的字段是交易输出的数额，即以聪为单位的比特币数量。此字段可以用来编码存储信息。

2019年9月，Check Point的研究人员发现Redaman开始利用区块链来隐藏CC地址。Redaman是针对俄语用户的通过钓鱼方式传播的银行恶意软件，最初于2015年被发现。CheckPoint的研究人员在其新版本中，发现其使用比特币区块链进行小马CC地址的隐藏。它通过对CC地址进行编码，转换为一个交易数字，通过给硬编码在Bot中的比特币地址转账，进行CC地址的传播。它的感染过程如下图。

[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01b6bdaf747585aeca.png)

**Redaman感染过程**

以IP 185.203.116.47和比特币地址1BkeGqpo8M5KNVYXW3obmQt1R58zXAqLBQ为例，具体对CC地址进行编码的过程如下。<br>
首先将IP地址由十进制转换为十六进制的形式：185.203.116.47 =&gt; B9.CB.74.2F。然后两字节一组，分别调换字节序，组成一个十六进制数字，如CBB9和2F74。把十六进制数字转换为十进制，分别为52153和12148。分别创建交易，给硬编码在Bot中的比特币地址转账这两个十进制数字大小的以聪为单位的比特币，即先创建一笔交易，给1BkeGqpo8M5KNVYXW3obmQt1R58zXAqLBQ转入52153 sat（0.00052153 BTC，约$4），待此交易确认后，再转入12148 sat（0.00012148 BTC，约$1），如下图。

[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c3dcf1cf6df249ef.png)

**交易示例**

对于Bot来说，可以通过比特币服务平台的API查询和被硬编码的比特币地址相关的交易，从交易中获取交易数额，进行上述过程的逆过程，组装成CC的IP。例如，获取到的交易数额分别为52153和12148，转换为十六进制为CBB9和2F74，再分别转换字节序进行拆分，得到B9、CB、2F和74，将其转换为十进制连接起来即可，即185.203.116.47。

由于涉及到数据的回传，在这个案例里面，还是引入了与区块链无关的通信信道，区块链的优势未完全发挥。此外，由于每个人都可以看到区块链上的交易，所有的CC地址会被研究人员分析出来，也会被永久记录在区块链上。而所有人都可以给这个地址转账，会增加外界干扰，引起僵尸网络失效或被take over。



## 椭圆曲线密码

比特币中使用的是椭圆曲线密码（Elliptic Curve Cryptography，ECC）来进行数字签名和身份认证。有一些Bot设计者利用椭圆曲线数字签名的一些问题进行CC。这里将简单介绍椭圆曲线密码算法、椭圆曲线数字签名算法和存在的问题，然后对Bot设计者的利用思路进行介绍。

### <a class="reference-link" name="%E6%A4%AD%E5%9C%86%E6%9B%B2%E7%BA%BF%E5%AF%86%E7%A0%81"></a>椭圆曲线密码

密码学上使用的椭圆曲线（Elliptic Curve，EC）通常为在整数域[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t018bbdfc5ffb52316d.png)（p为素数，p&gt;3）上形如 y^2≡x^3+a∙x+b mod p，其中a,b∈[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t017b94df3b46b4c361.png)，4a^3+27b^2≠0 mod⁡ p 的曲线，记为[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c19bd052c838f176.png)。椭圆曲线上的点包含所有满足等式的点(x,y)和一个无限远点O。

下图是实数域上的椭圆曲线y^2=x^3-3x+3。

[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t018d95a0ed6954bb23.png)

下图是整数域[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01f3df7004099df6eb.png)上椭圆曲线y^2≡x^3-3x+3 mod 11的图像。

[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01fd9785ece9d371fc.png)

包含无限远点O在内的曲线上的点构成一个循环子群。在一些条件下，椭圆曲线上的所有点可以形成一个循环群。

定义群运算“+”，已知椭圆曲线上的点[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01578e43284e973ffd.png)和[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01561f5532335f5db2.png)，[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t017a6bf4d79658bf80.png)为第三点，有

[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01c1857bcadfd530e1.png)

[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t017b418cb931a6bc68.png)

由此定义椭圆曲线离散对数问题（Elliptic Curved Discrete Logarithm Problem，ECDLP）：给定一个椭圆曲线E，记#E为[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01660b089b900f28ae.png)上的点的数量，考虑生成元P和另一个元素T，则离散对数问题为寻找一个整数d(1≤d≤#E)，满足

[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t019724c5bb931519e7.png)

通过将消息编码为曲线上的点，进行“+”运算实现对消息的加密。在密码系统中，d为私钥，(E,#E,P,T)为公钥。由d和P计算T比较简单，但由P和T计算d则比较困难。若选取非常大的椭圆曲线参数和私钥，则以现有的算力，在有限的时间内不能完成对d的破解，由此保证了数据的安全性。在实际使用中，为保证安全性，通常选取NIST推荐的标准曲线，选取160位以上的密钥。比特币密码算法中使用的ECC密钥为256位。

### <a class="reference-link" name="%E6%A4%AD%E5%9C%86%E6%9B%B2%E7%BA%BF%E6%95%B0%E5%AD%97%E7%AD%BE%E5%90%8D%E7%AE%97%E6%B3%95"></a>椭圆曲线数字签名算法

数字签名的定义为附加在数据单元上的数据，或是对数据单元所作的密码变换，这种数据或变换允许数据单元的接收者用以确认数据单元的来源和完整性，并保护数据防止被人伪造或抵赖。（《GB/T 25069-2010 信息安全技术 术语》）

数字签名算法通常由密钥生成、签名、验证三部分算法组成。密钥生成算法会确定签名方案的基本参数，包括公私钥对、重要参数（如大素数、随机数等）。签名算法将对消息进行数学上的操作与运算，得到消息的签名值。验证算法将针对消息和消息的签名值进行与签名过程对应的数学运算，验证签名是否真实有效。

椭圆曲线数字签名（Elliptic Curve Digital Signature Algorithm，ECDSA）的过程如下。

（1）密钥生成

选定[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0187729a01b5669cc0.png)，令q=#E，选择随机数d（0&lt;d&lt;q），选定E上能生成阶为q的循环群的点A，计算B=dA。<br>
密钥对如下：<br>[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0155c593a2a88c96f1.png)<br>[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t017660dddebbf357b8.png)

（2）签名

选择随机临时密钥[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e51780585a3e8bfd.png)（0&lt;[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c3320726e6418e2b.png)&lt;q），计算[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01feaa1dd89e438e9d.png)。令[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01f8b68178d746e8ec.png)，选取消息摘要（Hash）算法h(x)，计算[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01b3be3356bb4b8e84.png)。<br>
签名值为s，签名者需要发送的信息为 (x,(r,s))

（3）验证

计算辅助变量[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t015dcbd2ea1d42d39c.png)、[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t011c96f23cea8e4693.png)、[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0139d685bded1e271e.png)，计算[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01758a9d85016e1f8e.png)。<br>
验证<br>[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0166b84e131bdecd05.png)<br>[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01374dde34caea0a7c.png)

### <a class="reference-link" name="%E6%A4%AD%E5%9C%86%E6%9B%B2%E7%BA%BF%E6%95%B0%E5%AD%97%E7%AD%BE%E5%90%8D%E7%AE%97%E6%B3%95%E7%9A%84%E4%B8%B4%E6%97%B6%E5%AF%86%E9%92%A5%E9%87%8D%E7%94%A8%E6%94%BB%E5%87%BB"></a>椭圆曲线数字签名算法的临时密钥重用攻击

椭圆曲线数字签名算法要求每次签名使用的随机数[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t016db27f61df8a9b32.png)不能重复，否则会由两个签名消息推算出签名所用的私钥，造成私钥泄露。<br>
具体地，令第一次签名的消息为[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01362011037ef167f8.png)，得到的签名值为[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01c130974bcccfeee3.png)；第二次签名的消息为[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t017101583e1df3e044.png)，得到的签名值为[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01a284477a5ab3c4de.png)；两次签名使用的随机数为[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01f0f51c5f334cd559.png)，私钥为d。则由ECDSA签名算法可得

[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t010e4dbfea0504be41.png)

[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0197b97fe64db98b4e.png)

则有

[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01876fb751d8fab3e6.png)

故

[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01732bc47019d80f6f.png)

继续计算可得

[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01edb6ffbae2bd9664.png)

[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t012a1937f3adc6b3f4.png)

于是

[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01479875ea25911ab2.png)

私钥d被泄露。



## 利用数字签名进行CC

### <a class="reference-link" name="%E7%A7%81%E9%92%A5%E5%8D%B3%E5%91%BD%E4%BB%A4"></a>私钥即命令

由于比特币中使用的ECC私钥长度为32字节，因此有人提出利用随机密钥重用的方法泄露出私钥，让Bot从私钥中获取命令。<br>
具体做法为，对命令进行编码，加入混淆后生成私钥，用此私钥生成公钥和比特币地址；使用这个比特币地址创建两个交易，对这两个交易使用相同的随机密钥进行签名，并先后发布。Bot需要监听一个比特币地址的交易，在发现两个交易公钥中的r相同时，保存交易内容，从中计算出私钥d，并按预先设置的解码规则解出命令。下表是比特币交易的签名字段组成。交易签名采用DER编码，可以很容易地检测出两个相同的r。

[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01500acc6fc53abeaf.png)

此方法的弊端是，任何人都能通过查看两个交易是否使用相同随机数来进行私钥的计算。比特币网络中会有一些交易发起者因大意等原因使用了相同的随机数进行签名。如果这些私钥被泄露，那么与这个地址相关的比特币存在被窃取的风险。所以比特币网络上有一些程序对交易进行监视，当发现某一地址的两个交易使用相同的随机数时，可以转移该地址的比特币。因此，这种方法会时刻被监视，泄露私钥，进而泄露命令，具备一定的风险。

[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0158f5adfd3c14a2ad.png)

随后，有研究人员基于秘密共享机制提出了改进方法，如上图。这种方法的基本思想是，如下所示，把比特币地址[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t016e54fbcd1df06b7f.png)的私钥d拆分成[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01ccf06205046dfb38.png)和[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0180dc04e17afd5577.png)两部分，[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01ccf06205046dfb38.png)预编码到Bot中，[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0180dc04e17afd5577.png)对应的比特币地址[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01f4e145ced6ecb476.png)预编码到Bot中；通过临时密钥重用泄露[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0180dc04e17afd5577.png)，Bot可由[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01ccf06205046dfb38.png)和X_2计算出d，并由d计算出比特币地址[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t016e54fbcd1df06b7f.png)；通过监听与[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t016e54fbcd1df06b7f.png)相关的交易，获取命令信息。

[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t016e26be7db5330259.png)

研究人员认为，这种方法会减少由泄露私钥带来的命令泄露的风险，也能隐藏实际发送命令的比特币地址[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t016e54fbcd1df06b7f.png)。在Bot未被分析时，无法从区块链上的信息恢复出[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0180dc04e17afd5577.png)，也无法得到地址[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t016e54fbcd1df06b7f.png)。然而，在Bot端被拿下后，分析人员仍能通过计算得到私钥d和发送命令的比特币地址[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t016e54fbcd1df06b7f.png)，也具有一定的风险。

### <a class="reference-link" name="%E7%A7%81%E9%92%A5%E5%8D%B3%E5%AF%86%E9%92%A5"></a>私钥即密钥

由于重用随机密钥会带来较大的异常，研究人员提出了避免随机密钥重用的方法，如下图。此方法需要把一个[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t010b283e7650350e92.png)和比特币地址[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t015034cb5a52fd34ae.png)预编码到Bot中。

对命令发送者来说，把命令信息加密后保存在交易中；使用不同的随机数k生成不同的交易签名(r,s)；对于最后一个交易，使用[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t010b283e7650350e92.png)作为随机数进行签名；发送交易到区块链网络，等待上一个交易被确认上链后再发送下一个交易。

对于Bot来说，需要监听每一个与[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01ee76e489cd285ee0.png)相关的交易，对于每个交易，根据[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t010b283e7650350e92.png)计算一个可能的私钥值d’，并根据d’计算出一个比特币地址A’。若A’≠[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01ee76e489cd285ee0.png)，则保存此交易，继续监听区块链信息。若A’=[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01ee76e489cd285ee0.png)，则使用此d’作为密钥，解密保存的交易，获取命令。

[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01a605c8f342142e16.png)

[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t015a52585157c2fdd1.png)

这种做法略显复杂，相当于结合了利用交易脚本和利用随机数重用两种方法。但正是因为这种复杂的结合，使这种方法规避了其他方法的一些问题。比如，相对于使用交易脚本进行CC来说，即使Bot端不可靠，在发出最后一个交易之前，分析人员也不能从已有的交易中获取命令信息；相比Glupteba而言，这种方法不需要在Bot中硬编码对称密钥，而32字节的d作为对称密钥也足够安全；相对与直接利用临时密钥重用恢复私钥来说，这种方法不会区块链上留下使用相同随机密钥的记录，也规避了一部分监视。理论上，这种方法可以发送无限长的命令。命令发送者可以在发布的命令中嵌入下一个要监视的比特币地址[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01de4337f147d753b5.png)和新的随机数[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t019ef1382348a17227.png)，这样可以在私钥泄露以后弃用当前的比特币地址，一定程度上规避了该地址被分析人员利用后给Bot设施带来的风险。

这种方法也有一定的局限性。携带命令的OP_RETURN类型的交易均和一个比特币地址相关，会引起一定的异常。虽然不能被解密，但这种交易也会被区块链永久记录。Bot需要不断轮询获取与预设的比特币地址相关的交易，需要在宿主机上进行一定量的计算来匹配d’、A’和解密命令，这些网络与文件行为可能会引起异常。另外，此方法也没有提供合适的数据回传机制，在面临Bot端需要回传数据的情况时仍需其他方法配合。

### <a class="reference-link" name="%E7%AD%BE%E5%90%8D%E5%8D%B3%E5%91%BD%E4%BB%A4"></a>签名即命令

与上述两种方法不同的是，这种方法不需要利用椭圆曲线数字签名的临时密钥重用攻击。这种方法的思想是，使用不同的随机数，使产生的签名的前x位为命令。这种方法不会引起区块链上的异常，也不必使用OP_RETURN字段，但每个交易能嵌入的命令长度大大受限，而且会有一定的计算量。在面对较长的命令时，需将命令拆分成多个交易进行下发。

在ZombieCoin中，作者对此方法进行了实验。实验环境为Intel i7 2.8GHz 8GB RAM的64位Windows 7设备，使用OpenSSL工具集生成ECDSA签名。实验结果如下图。在单线程顺序搜索的情况下，当指定签名的前14位时，需要大约10分钟完成签名生成。在多线程顺序搜索的情况下，需要大约3分钟。在多线程非顺序搜索的情况下，需要大约2分钟。

[![](./img/199465/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01f15eafc0287ee5ae.png)

这种方法的优点在于不会引起交易和区块链的异常。其缺点有以下几点。当Bot被分析时，分析人员仍可以对所下发的一切命令进行追踪，这些信息也会被区块链永久记录。由于每个交易能携带的信息有限，这种方法可能需要创建多个交易来发送一条命令，较为繁琐，而且过多的交易会消耗更多的手续费。如果要提高交易携带的信息长度，需要控制端消耗一定的计算量。这种方法也没有考虑Bot信息回传的功能。



## 展望

使用比特币区块链做CC的这些方法中，均存在一些尚未解决的问题，如Bot网络行为异常、Bot信息无法回传、交易携带信息少、命令被永久记录在链等。面对这些问题，一些人员提出了使用智能合约、比特币测试链Testnet等进行CC的方法。比如以太坊智能合约中，命令的长度不受限，可以发布更长的命令；比特币测试链相对比特币主链具有更少的限制，可以更容易地获取币，能解决Bot数据回传的问题，也可以发布更长的命令。此外，无论是比特币还是智能合约，这些数字货币中均使用了椭圆曲线密码算法，故本文中提到的利用椭圆曲线数字签名问题进行CC的方法也同样适用于其他币种。除此之外，从目前曝光的案例来看，区块链只是CC活动中的一部分，使用者往往结合区块链和其他方法一起使用，以此利用区块链的特性并规避区块链的缺陷。关于检测利用比特币区块链做CC的活动，目前也有国外研究人员提出了一些方法，但从实验来看，效果并不明朗。



## 小结

本文总结了目前利用比特币区块链进行CC的方法，主要有利用交易脚本、交易值和数字签名等几类方法。从目前的分析来看，把命令编码在交易脚本的做法比较灵活，能以较少的开销传递更多的信息，但需要创建很多OP_RETURN类型的交易。利用交易值传递信息的方法只需创建普通的交易即可，但传递的信息量有限。利用ECDSA随机密钥重用泄露信息的方法可以以任何交易的形式存在，但这种方法存在泄露私钥的风险；如果对应的比特币地址和私钥在使用一次后就更换，则此方法还是可以考虑的。利用“私钥即密钥”方式进行CC的方法，理论上可以在传递无限长的命令，并且不会在比特币区块链上造成太大的异常，但此方法的计算量稍大。利用签名值隐藏命令的方法操作较为容易，但携带的信息实在有限，需要在命令编码与格式上花费功夫才能使用得当。本文还对使用区块链做CC进行了展望，汇集了一些学术界与工业界的相关拓展。从目前的观察来看，使用区块链做CC的方法比较明确，相关的技术也比较成熟。笔者认为，也许区块链不能承担起完整的CC过程，但如果使用巧妙得当，区块链能在CC或APT活动中发挥出更大价值。我们拭目以待。



## 致谢

在本文的创作过程中，山城安全和ArkTeam提供了很大帮助，提出了众多有价值的意见和建议，在此致谢！



## 参考资料

1.KLmoney. “Bitcoin: Dissecting Transactions.” [https://klmoney.wordpress.com/bitcoin-dissecting-transactions/](https://klmoney.wordpress.com/bitcoin-dissecting-transactions/)<br>
2.Bitcoin Wiki. “Script.” [https://en.bitcoin.it/wiki/Script](https://en.bitcoin.it/wiki/Script).<br>
3.Ali, Syed Taha, et al. “ZombieCoin: Powering Next-Generation Botnets with Bitcoin.” (2015).<br>
4.Ali, Syed Taha, et al. “ZombieCoin 2.0: managing next-generation botnets using Bitcoin.” (2018).<br>
5.Kobi Eisenkraft, et al. “Pony’s C&amp;C servers hidden inside the Bitcoin blockchain.” [https://research.checkpoint.com/2019/ponys-cc-servers-hidden-inside-the-bitcoin-blockchain/](https://research.checkpoint.com/2019/ponys-cc-servers-hidden-inside-the-bitcoin-blockchain/)<br>
6.Paar, Christof, et al. “Understanding Cryptography.” (2010).<br>
7.Jaromir Horejsi, et al. “Glupteba Campaign Hits Network Routers and Updates C&amp;C Servers with Data from Bitcoin Transactions.” [https://blog.trendmicro.com/trendlabs-security-intelligence/glupteba-campaign-hits-network-routers-and-updates-cc-servers-with-data-from-bitcoin-transactions/](https://blog.trendmicro.com/trendlabs-security-intelligence/glupteba-campaign-hits-network-routers-and-updates-cc-servers-with-data-from-bitcoin-transactions/).<br>
8.Frkat, Davor, et al. “ChainChannels: Private Botnet Communication Over Public Blockchains.” (2018).<br>
9.Jonathan Sweeny. “Tearing up Smart Contract Botnets.” (2018)<br>
10.Franzoni, Federico, et al. “Leveraging Bitcoin Testnet for Bidirectional Botnet Command and Control Systems.” (2020).<br>
11.Zarpelao, Bruno Bogaz, et al. “Detection of Bitcoin-Based Botnets Using a One-Class Classifier.” (2019)

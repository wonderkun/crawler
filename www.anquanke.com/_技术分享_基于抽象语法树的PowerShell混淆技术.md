> 原文链接: https://www.anquanke.com//post/id/87329 


# 【技术分享】基于抽象语法树的PowerShell混淆技术


                                阅读量   
                                **153012**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：cobbr.io
                                <br>原文地址：[https://cobbr.io/AbstractSyntaxTree-Based-PowerShell-Obfuscation.html](https://cobbr.io/AbstractSyntaxTree-Based-PowerShell-Obfuscation.html)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p3.ssl.qhimg.com/t0169e2314f39c88b4b.jpg)](https://p3.ssl.qhimg.com/t0169e2314f39c88b4b.jpg)**

****

译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**一、前言**



在最新发布的[PSAmsi](https://github.com/cobbr/PSAmsi) v1.1版本中，最大的变化就是增加了基于AbstractSyntaxTree（抽象语法树）的PowerShell“混淆”功能。这里“混淆”一词打了引号，希望大家阅读完本文后能理解这个引号的含义。

**<br>**

**二、AbstractSyntaxTree简介**



什么是AbstractSyntaxTree（抽象语法树，AST）？AST是一种常用结构，可以通过树状表现形式来分析、解析编译型语言以及解释型语言的源代码。PowerShell从v3以来就引入了AST功能。与其他语言相比，PowerShell的独特之处在于，该语言提供的AST结构非常便于开发者使用，并且相关的[文档](https://docs.microsoft.com/en-us/dotnet/api/system.management.automation.language)也非常翔实。

一个PowerShell脚本可以对应一个完整的AbstractSyntaxTree结构，如下所示：[![](https://bobao.360.cn/ueditor/themes/default/images/spacer.gif)](https://bobao.360.cn/ueditor/themes/default/images/spacer.gif)

[![](https://p2.ssl.qhimg.com/t01d9429360ecaefc2d.png)](https://p2.ssl.qhimg.com/t01d9429360ecaefc2d.png)

**<br>**

**三、示例脚本**



在下文中，我们会以如下脚本为例来介绍相关知识点：[![](https://bobao.360.cn/ueditor/themes/default/images/spacer.gif)](https://bobao.360.cn/ueditor/themes/default/images/spacer.gif)

[![](https://p1.ssl.qhimg.com/t01c13b3766ad09b3d2.png)](https://p1.ssl.qhimg.com/t01c13b3766ad09b3d2.png)

这个PowerShell函数并没有什么实际功能，但有助于我们理解基于AST的一些混淆技术。

**3.1 基于PSToken的混淆技术**



为了理解基于AST混淆技术的优点，我觉得我们可以先来了解一下基于PSToken混淆技术的工作原理。Token或者“PSToken”是另一种语法结构，可以用来解析并表示PowerShell代码，PowerShell从v2开始就引入了这个功能。PowerShell脚本实际上由大量PSToken所组成，这些PSToken之间通常以空格符隔开。AST通常以较为复杂的结构形式来表示脚本，并且会根据函数组件来分组，而PSToken则采用了更为简单的列表形式。

在v1.0版的PSAmsi中，唯一使用的混淆技术为[Invoke-Obfuscation](https://github.com/danielbohannon/Invoke-Obfuscation)的“Token”混淆技术，这是一种基于PSToken的混淆技术。Invoke-Obfuscation提供了各种选项，可以用来混淆各种类型的PSToken。从顶层视角来看，该技术会遍历脚本中的所有PSToken，单独混淆处理每个PSToken，最后将混淆后的片段重新组合起来。

比如，上面这个示例脚本所对应的PSToken混淆过程如下所示：

首先是遍历所有PSToken，第一个是CommandArgument类型的token。PowerShell中，我们可以在CommandArgument类型的token中插入一些特殊符号，如下所示：



```
Type            Content                     ObfuscatedContent
----            -------                     -----------------
CommandArgument Test-AstObfuscation   -&gt;    TE`s`t-AS`TOBFus`CAtIon
```

接下来，我们面对的是一个Member类型的ParameterSetNametoken，这种token中无法插入特殊符号，因此我们可以随机化其中包含的字符。



```
Type            Content                     ObfuscatedContent
----            -------                     -----------------
CommandArgument Test-AstObfuscation   -&gt;    TE`s`t-AS`TOBFus`CAtIon
Member          ParameterSetName      -&gt;    ParamEterseTNAME
```

接下来是一个String类型的token，这种类型的token有一些混淆方法，这里我们直接加入一些特殊符号，如下所示：



```
Type            Content                     ObfuscatedContent
----            -------                     -----------------
CommandArgument Test-AstObfuscation   -&gt;    TE`s`t-AS`TOBFus`CAtIon
Member          ParameterSetName      -&gt;    ParamEterseTNAME
String          Set1                  -&gt;    “S`et1”
```

这种迭代过程会贯穿整个脚本：



```
Type            Content                                  ObfuscatedContent
----            -------                                  -----------------
CommandArgument Test-AstObfuscation              -&gt;      TE`s`t-AS`TOBFus`CAtIon
Member          ParameterSetName                 -&gt;      ParamEterseTNAME
String          Set1                             -&gt;      “S`et1”
Member          Position                         -&gt;      PositiOn
Member          Mandatory                        -&gt;      MAnDatoRY
Member          ValueFromPipelineByPropertyName  -&gt;      ValUefroMPipELiNebyProPeRTyname
Variable        True                             -&gt;      $`{`t`RuE`}`             
String          Parameter1                       -&gt;      `{`“`{`0`}``{`1`}``{`2`}`” –f’Parame’,’te’,’r1’`}`
String          Param1                           -&gt;      `{`“`{`1`}``{`0`}`”-f’1’,’Param’`}`
String          ParamOne                         -&gt;      `{`”`{`0`}``{`2`}``{`1`}`” –f ‘Para’,’e’,’mOn’`}`
Variable        ParameterOne                     -&gt;      $`{`p`Ara`m`et`EROne`}`
Member          ParameterSetName                 -&gt;      PaRamEtERsEtNaME
String          Set2                             -&gt;      “SE`T2”
Member          Position                         -&gt;      POSitiON
...
```

最终生成的结果如下所示：[![](https://bobao.360.cn/ueditor/themes/default/images/spacer.gif)](https://bobao.360.cn/ueditor/themes/default/images/spacer.gif)

[![](https://p5.ssl.qhimg.com/t01aeb656b2d1f33320.png)](https://p5.ssl.qhimg.com/t01aeb656b2d1f33320.png)

Invoke-Obfuscation中集成的这种PSToken混淆技术在绕过AMSI（反恶意软件扫描接口）特征检测机制方面卓有成效（实际上，我所见到的基于PSToken的混淆技术都可以绕过AMSI机制）。然而，这种混淆技术也有一些缺点，可以被某些混淆检测机制检测到，大家可以参考我前面写的一篇[文章](https://cobbr.io/PSAmsi-Minimizing-Obfuscation-To-Maximize-Stealth.html)。基于PSToken的混淆技术添加了许多特殊符号，采用了一些比较奇怪的PowerShell语法，而实际攻击中出现这种情况就比较容易引人注意。

在PSAmsi v1.0中，我们的目标是针对性地使用基于PSToken的混淆技术，将好钢用在刀刃上，而不是在整个脚本中应用这种技术，通过这种方式来弥补这种技术的不足。这种方法的确可以发挥作用，但我们是否可以进一步改进？

**3.2 基于AST的混淆技术**



在PSAmsi v1.1版中，我添加了一个函数：[Out-ObfuscatedAst](https://github.com/cobbr/PSAmsi/blob/master/PSAmsi/Obfuscators/PowerShell/Out-ObfuscatedAst.ps1)，这个函数利用AST的强大功能实现了更为隐蔽的混淆技术。基于AST的混淆技术中最关键的一点在于，这种技术采用了AST类型，该类型可以作为整体树形结构中子元素，扮演上下文环境角色，为其他混淆方法提供服务。这些混淆方法大多与脚本中的AST顺序有关。我们可以通过一个例子来理解这一点。

示例脚本所对应的整个树形结构非常庞大，无法优雅地在文中表示出来，因此我们先来看看其中的一小部分结构，如下所示：[![](https://bobao.360.cn/ueditor/themes/default/images/spacer.gif)](https://bobao.360.cn/ueditor/themes/default/images/spacer.gif)

[![](https://p1.ssl.qhimg.com/t01fdf72e5568f8b00c.png)](https://p1.ssl.qhimg.com/t01fdf72e5568f8b00c.png)

这是一种AttributeAst，对应脚本中的一行语句，通过各种属性值来表示ParamBlockAst中的某个参数。这个Ast中包含4个子节点，这些节点为该参数目前具备的所有属性。其中有个属性为”Mandatory“属性，这表明调用该函数时必须使用该参数。Mandatory属性为布尔（boolean）类型，值为True或者False。在PowerShell中，我们可以直接使用名称（如“Mandatory“）来指定True值布尔属性，或者可以通过赋值True达到相同目的（比如“Mandatory = $True”）。目前，我们使用的是名称表示法，现在我们可以稍作改变：[![](https://bobao.360.cn/ueditor/themes/default/images/spacer.gif)](https://bobao.360.cn/ueditor/themes/default/images/spacer.gif)

[![](https://p4.ssl.qhimg.com/t015c06f49d12cbab5d.png)](https://p4.ssl.qhimg.com/t015c06f49d12cbab5d.png)

这种方法也可以应用于“ValueFromPipelineByPropertyName”属性，这次我们砍掉其中的“= $True”，只留下属性名：[![](https://bobao.360.cn/ueditor/themes/default/images/spacer.gif)](https://bobao.360.cn/ueditor/themes/default/images/spacer.gif)

[![](https://p1.ssl.qhimg.com/t016e86eba40f8ac133.png)](https://p1.ssl.qhimg.com/t016e86eba40f8ac133.png)

最后，剩下的所有子节点对应变量中互不相关的一些属性，因此我们可以随意排列这些节点的顺序：[![](https://bobao.360.cn/ueditor/themes/default/images/spacer.gif)](https://bobao.360.cn/ueditor/themes/default/images/spacer.gif)

[![](https://p2.ssl.qhimg.com/t014a2f5aa7768f3399.png)](https://p2.ssl.qhimg.com/t014a2f5aa7768f3399.png)

从这里开始，我们可以理解树状结构中的AST元素在混淆方面所起的作用。`AttributeAst` 中子节点代表某个参数的属性，基于这一点，我们可以在同一个`AttributeAst`中重新排列这些参数。

现在，我们可以拉高视角，看看规模大点的树：[![](https://bobao.360.cn/ueditor/themes/default/images/spacer.gif)](https://bobao.360.cn/ueditor/themes/default/images/spacer.gif)

[![](https://p4.ssl.qhimg.com/t01394d623f028dcf48.png)](https://p4.ssl.qhimg.com/t01394d623f028dcf48.png)

这是原始树结构，我们前面分析的`AttributeAst` 为该树中的一个节点。因此，我们先按上面的方法处理这个`AttributeAst`节点。[![](https://bobao.360.cn/ueditor/themes/default/images/spacer.gif)](https://bobao.360.cn/ueditor/themes/default/images/spacer.gif)

[![](https://p1.ssl.qhimg.com/t01ca379075fd8b07ae.png)](https://p1.ssl.qhimg.com/t01ca379075fd8b07ae.png)

现在，我们继续处理带有“Alias”（别名）的`AttributeAst` 。这个`AttributeAst` 指定了默认的“ParameterOne”参数名的别名。我们也可以任意排列这些别名的顺序，如下所示：[![](https://bobao.360.cn/ueditor/themes/default/images/spacer.gif)](https://bobao.360.cn/ueditor/themes/default/images/spacer.gif)

[![](https://p0.ssl.qhimg.com/t01be7ccc301448105a.png)](https://p0.ssl.qhimg.com/t01be7ccc301448105a.png)

再次拉高视角，观察更大规模的树结构：[![](https://bobao.360.cn/ueditor/themes/default/images/spacer.gif)](https://bobao.360.cn/ueditor/themes/default/images/spacer.gif)

[![](https://p0.ssl.qhimg.com/t01d3c74b59135008e7.png)](https://p0.ssl.qhimg.com/t01d3c74b59135008e7.png)

可以看到，大一点的ParamBlockAst中包含两个参数。目前为止，我们关注的是ParameterOne这个参数。现在，我们可以将前面用到的混淆技巧用到这个参数上。[![](https://bobao.360.cn/ueditor/themes/default/images/spacer.gif)](https://bobao.360.cn/ueditor/themes/default/images/spacer.gif)

[![](https://p1.ssl.qhimg.com/t01c2844ff6690ae22f.png)](https://p1.ssl.qhimg.com/t01c2844ff6690ae22f.png)

当然，我们也可以将这种处理方法用在第二个参数ParameterTwo上。我们可以重新排列ParameterTwo中`AttributeAst` 中的属性，就像第一个参数中的混淆过程一样：[![](https://bobao.360.cn/ueditor/themes/default/images/spacer.gif)](https://bobao.360.cn/ueditor/themes/default/images/spacer.gif)

[![](https://p1.ssl.qhimg.com/t01a6e2f55d032841ad.png)](https://p1.ssl.qhimg.com/t01a6e2f55d032841ad.png)

但其实这两个参数本身的顺序也可以调换，因此我们可以调换ParamBlockAst中`ParameterAst`的顺序：[![](https://bobao.360.cn/ueditor/themes/default/images/spacer.gif)](https://bobao.360.cn/ueditor/themes/default/images/spacer.gif)

[![](https://p0.ssl.qhimg.com/t016ed1506e1c18ba32.png)](https://p0.ssl.qhimg.com/t016ed1506e1c18ba32.png)

现在，我们最后一次拉高视角：[![](https://bobao.360.cn/ueditor/themes/default/images/spacer.gif)](https://bobao.360.cn/ueditor/themes/default/images/spacer.gif)

[![](https://p1.ssl.qhimg.com/t0149f6f6204ebd1138.png)](https://p1.ssl.qhimg.com/t0149f6f6204ebd1138.png)

前面我们分析的`ParamBlockAst` 都包含在这个`ScriptBlockAst`中，此外，这个`ScriptBlockAst`中还包含其他3个`NamedBockAst`子节点。我们可以先把前面发现的混淆方法用在`ParamBlockAst`上：[![](https://bobao.360.cn/ueditor/themes/default/images/spacer.gif)](https://bobao.360.cn/ueditor/themes/default/images/spacer.gif)

[![](https://p2.ssl.qhimg.com/t01be99b83afd4de10f.png)](https://p2.ssl.qhimg.com/t01be99b83afd4de10f.png)

现在，我们先把视角集中在第一个`NamedBlockAst`子节点上，这个子节点包含“Begin”代码块。这个代码块的唯一功能是将最大值与最小值之间的一个随机值赋值给“Start”变量。在PowerShell中，除了使用标准的“=”操作符之外，我们还可以使用其他方法来给变量赋值，比如，我们可以使用`Set-Variable`这个cmdlet。此外，命名参数（比如`Get-Random`所使用的`-Minimum`以及`-Maximum`参数）的使用顺序可以随意调换。因此，我们可以使用`Set-Variable`、交换`-Minimum`以及`-Maximum`参数的顺序，通过这些方法进行混淆：[![](https://bobao.360.cn/ueditor/themes/default/images/spacer.gif)](https://bobao.360.cn/ueditor/themes/default/images/spacer.gif)

[![](https://p3.ssl.qhimg.com/t01806ae77d259c0f83.png)](https://p3.ssl.qhimg.com/t01806ae77d259c0f83.png)

接下来看第二个`NamedBlockAst` 子节点，即“Process”代码块，对于其中的“Result”变量，我们也可以使用`Set-Variable` 来完成变量赋值。此外，变量复制操作中，我们还可以看到一些数字表达式（比如数字的加法运算符），这些操作满足交换律，我们也可以对这些表达式进行重新排序。因此，我们可以将这些混淆方法用在这段代码上：[![](https://bobao.360.cn/ueditor/themes/default/images/spacer.gif)](https://bobao.360.cn/ueditor/themes/default/images/spacer.gif)

[![](https://p0.ssl.qhimg.com/t0177f9d92fb20b7459.png)](https://p0.ssl.qhimg.com/t0177f9d92fb20b7459.png)

最后，我们可以重新排列该函数中`ScriptBlockAst`中的Begin、Process以及End代码块的顺序，如下所示：[![](https://bobao.360.cn/ueditor/themes/default/images/spacer.gif)](https://bobao.360.cn/ueditor/themes/default/images/spacer.gif)

[![](https://p4.ssl.qhimg.com/t01b7b8d865b8579a42.png)](https://p4.ssl.qhimg.com/t01b7b8d865b8579a42.png)

经过这些处理后，利用`Out-ObfuscatedAst`我们能得到如下结果：[![](https://bobao.360.cn/ueditor/themes/default/images/spacer.gif)](https://bobao.360.cn/ueditor/themes/default/images/spacer.gif)

[![](https://p1.ssl.qhimg.com/t01d5b5040c47f78e5a.png)](https://p1.ssl.qhimg.com/t01d5b5040c47f78e5a.png)

读到这里，希望大家能理解为什么我给“混淆”这个词打上引号。基于AST的这种混淆技术并不能掩盖脚本的真正功能，只是通过重新排列树结构中的子节点，得到功能上相同的代码，这些代码与源代码看起来有所不同。虽然这种技术不能彻底掩盖代码的功能，但足以破坏基于特征的检测机制。

基于AST的混淆技术中最酷的一点在于，这种方法并不需要使用许多特殊字符或者奇怪的语法来完成混淆任务。从整体上来看，这种方法生成的PowerShell看起来非常正常，因此任何混淆检测机制都难以检测这种技术。我当然可以在AST混淆技术中加入一些特殊字符以及奇怪语法，但我觉得这些功能还是保留在PSToken混淆技术中比较好。如果你想鱼和熊掌兼得，你可以亲自动手试一下，结果看起来比较吓人：[![](https://bobao.360.cn/ueditor/themes/default/images/spacer.gif)](https://bobao.360.cn/ueditor/themes/default/images/spacer.gif)

[![](https://p2.ssl.qhimg.com/t014ac13ab88304392f.png)](https://p2.ssl.qhimg.com/t014ac13ab88304392f.png)

当然，`Out-ObfuscatedAst` 还有许多改进空间。目前这种技术已经可以绕过大量特征检测机制，但AST本身是一种非常强大的结构，我相信PowerShell函数中还可以使用基于AST的其他新型混淆技术。我会继续尝试，不断添加新型混淆方法。

**<br>**

**四、关于PSAmsi**



在此之前，PSAmsi的目标采用的是基于PSToken的混淆技术，使用最少的混淆量来混淆代码中需要处理的特征，以绕过混淆检测技术。现在，我们不仅能够混淆需要处理的代码特征，也可以在代码中使用隐蔽的AST混淆技术。

在PSAmsi中，`Get-MinimallyObfuscated`函数的处理过程如下：

1、首先，枚举脚本中的代码特征；

2、其次，迭代处理每个代码特征。对于每个代码特征，我们会尝试基于AST的混淆技术，这种技术通常能够去掉代码特征，但偶尔会有漏网之鱼；

3、最后，如果无法使用基于AST的混淆技术，我们会使用基于PSToken的混淆技术。

通过这种方法，我们能将代码中使用的混淆量限制在一定规模内，同时还能去掉给定脚本中的代码特征。

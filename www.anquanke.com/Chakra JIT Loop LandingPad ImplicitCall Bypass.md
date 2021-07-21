> 原文链接: https://www.anquanke.com//post/id/163315 


# Chakra JIT Loop LandingPad ImplicitCall Bypass


                                阅读量   
                                **151291**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/dm/1024_512_/t01b3ebebbb57324269.jpg)](https://p4.ssl.qhimg.com/dm/1024_512_/t01b3ebebbb57324269.jpg)

Author: Qixun Zhao(aka @S0rryMybad &amp;&amp; 大宝) of Qihoo 360 Vulcan Team

## 前言

在[第一篇文章](https://blogs.projectmoon.pw/2018/08/17/Edge-InlineArrayPush-Remote-Code-Execution/)的时候,我们提到过关于回调的漏洞一般分为三种情况,其中第一种是GlobOpt阶段的|BailOutOnImplicitCall| bailoutKind没有加入.具体来说就是在GlobOpt阶段遍历处理每一个opcode的时候,chakra会检测这个opcode是否有必要加上此bailoutKind,如果加上了,在Lower阶段生成出的指令中会在指令结束的时候检测一个implicit call flag，在发生回调的时候这个flag设置为true,JIT生成的检测指令如果检测到为true就会bailout,用于在回调发生的时候bailout。

今天我们要介绍的是[CVE-2018-8456](https://github.com/Microsoft/ChakraCore/commit/98360625854f84262ce8de59a7f57496393281f3),这个漏洞的原理有点复杂,我的表达可能会不太清楚,希望大家能坚持看下去:)



## Check Or Not Check?

我们知道,在很多情况下,上述的implicit call flag check指令是没有必要生成的,所以有一个专门的函数决定当前opcode是否生成|BailOutOnImplicitCall| bailoutKind,这个函数是|IsImplicitCallBailOutCurrentlyNeeded|.

[![](https://blogs.projectmoon.pw/2018/10/26/Chakra-JIT-Loop-LandingPad-ImplicitCall-Bypass/1.png)](https://blogs.projectmoon.pw/2018/10/26/Chakra-JIT-Loop-LandingPad-ImplicitCall-Bypass/1.png)

我们可以看到高亮的地方,对应的参数是|mayNeedImplicitCallBailOut|,如果为false,这个指令必定不会生成|BailOutOnImplicitCall|,换句话说,如果当前block |IsLandingPad|为true,当前block上所有的指令都不会生成check.这里我们有必要了解一些编译原理的相关术语block和LandingPad



## What is LandingPad

在编译原理中,CFG(控制流程图)中的最小单位是block,每一个不同的流程都会分裂出一个block,而block也是JIT中很喜欢进行优化的一个单元(我们可以看到optblock等等的函数),block组成function,opcode组成block.而LandingPad是针对Loop(循环)优化而生成的一个子block,用于存放loop中一定保持不变的变量的相关指令,也就是没有必要每一次循环都调用的指令.举个具体的例子,看如下js代码:

[![](https://blogs.projectmoon.pw/2018/10/26/Chakra-JIT-Loop-LandingPad-ImplicitCall-Bypass/2.png)](https://blogs.projectmoon.pw/2018/10/26/Chakra-JIT-Loop-LandingPad-ImplicitCall-Bypass/2.png)

我们知道数组每一次的访问都是需要load field,type check, bound check等等,然后再赋值,但是这里很明显type check和bound check都是可以提取到loop body外面,只需要在循环开始的时候检查一次就可以了,否则会浪费很多时间执行没必要的检查,这个在chakra称为|Loop hoist|.用于存放这些只需要在循环开始运行一次的指令的block就称为|LandingPad|,在这个区域中生成的任何指令都不会进行implicit call check.

但是很明显不是每一个opcode都是可以hoist到|LandingPad|的,用于决定函数是否可以hoist的函数是|TryHoistInvariant| =&gt; |OptIsInvariant|.简单来说就是,如果chakra觉得opcode的所有src都是不变量并且opcode带有CanCSE的属性,这个opcode就会被hoist.通过简单审阅一遍,我发现能hoist的指令的条件十分苛刻,主要在CanCSE属性和要求Src的Type |IsPrimitive|为true这两点上:

[![](https://blogs.projectmoon.pw/2018/10/26/Chakra-JIT-Loop-LandingPad-ImplicitCall-Bypass/3.png)](https://blogs.projectmoon.pw/2018/10/26/Chakra-JIT-Loop-LandingPad-ImplicitCall-Bypass/3.png)

这几乎把所有能回调的opcode都封掉了.其实这也很正常,如果带有回调,opcode的dst就肯定不会为不变量.所以这里我们需要转换思路.



## Give me a callback in LandingPad

CSE是一种常见的编译器优化措施,用于消除一些可以取代的公共子表达式,但是带有回调的opcode是不可以通过CSE措施消除的,因为带有回调往往就表示这个opcode产生的结果不会是不变量.既然不能直接hoist,那么我们能不能用已经hoist的指令生成一个新的带有回调的指令呢,事实证明这个思路是可行的.我在审阅|OptHoistInvariant|的过程中,出现一种情况会生成一个新的opcode(OptHoistInvariant=&gt;OptHoistUpdateValueType):

[![](https://blogs.projectmoon.pw/2018/10/26/Chakra-JIT-Loop-LandingPad-ImplicitCall-Bypass/4.png)](https://blogs.projectmoon.pw/2018/10/26/Chakra-JIT-Loop-LandingPad-ImplicitCall-Bypass/4.png)

我们可以看到,|SetConcatStrMultiItemBE|有一个逻辑会生成|Conv_PrimStr|,并且这个opcode带有|OpOpndHasImplicitCall|属性,说明它是有可能回调的.聪明的读者在这里可能也会提问为什么我们不直接插入|Conv_PrimStr|到LandingPad.这里因为要产生回调src必须不为Primitive,但是上文已经提到,如果|IsPrimitive|为false,这个指令是不可以hoist的,所以这里通过这种曲线救国的方法hoist上去.



## What is your src’s TYPE, Conv_PrimStr?

接下来是此漏洞最关键的地方.<br>
所以为什么通过|SetConcatStrMultiItemBE|hoist上去的|Conv_PrimStr|就可能不为Primitive?首先我们需要看函数|OptHoistUpdateValueType|的逻辑,正如函数名字那样,因为在hoist的过程中,这个opcode是需要从一个block转移到另一个block上(LandingPad),所以opcode的src type是需要更新的,因为type check指令可能存在与这两个block之间,如果hoist到type check指令之前,type要变为Likely.还是举个例子:

[![](https://blogs.projectmoon.pw/2018/10/26/Chakra-JIT-Loop-LandingPad-ImplicitCall-Bypass/5.png)](https://blogs.projectmoon.pw/2018/10/26/Chakra-JIT-Loop-LandingPad-ImplicitCall-Bypass/5.png)

这里我们给var1变量的profile feed一个string类型,然后调用它的|slice|函数,在调用的时候需要type check string, type check完成后,在这个block中余下的地方,var1 这个value的type都是|Definite String|,所以|IsPrimitive|为true,并且其他两个相加的变量都是常量字符串,这样可以保证了每一次循环中|let tmp2 = var1 + ‘projectmoon’ + ‘projectmoon’;|tmp2得到的结果都是一样的,完全可以hoist到loop body外面,从而|SetConcatStrMultiItemBE|会hoist到LandingPad,由于LandingPad在slice调用以前,也就是在type check string之前,所以这个时候的var1变量的type必须从|Definite String|变成|Likely String|.而|OptHoistUpdateValueType|就是专门负责这种情况的:<br>[![](https://blogs.projectmoon.pw/2018/10/26/Chakra-JIT-Loop-LandingPad-ImplicitCall-Bypass/6.png)](https://blogs.projectmoon.pw/2018/10/26/Chakra-JIT-Loop-LandingPad-ImplicitCall-Bypass/6.png)

由于现在var1还没有经过slice函数调用,也就是没有经过type check string,所以它可能是非String类型的变量,所以这里还需要加入一个|Conv_PrimStr| opcode,用于把非String类型转换成String,正如上文提到的(因为SetConcatStrMultiItemBE要求传入的src都是String),这个指令有可能生成回调,同时它的src type |IsPrimitive|为false,按照chakra的设计,它是不可以出现在LandingPad区域的,但是通过这个trick我们得到了这样的环境.



## 构造PoC

有了上文提到的要点后,我们可以开始构造PoC,首先是生成|SetConcatStrMultiItemBE|,这个是通过三个String相加生成(就如上图的例子),这里我们使用var1 + “constString” + “constString”生成.其次var1变量必须是String类型(IsPrimitive为true),这样才能hoist到LandingPad.这里我们通过调用var1.slice在String相加之前进行type check,从而保证了var1在|SetConcatStrMultiItemBE|这里的type是|definite String|,这里才能保证hoist成功.

这里还有一个问题就是type check指令的hoist(在chakra master版本有这个问题,正式版本中没有),由于string.slice()需要进行type check,而chakra也认为这个type check可以hoist到LandingPad中(事实也应该如此),从而会导致我们的变量在LandingPad进入|Conv_PrimStr|之前type check失败,然后发生bailout,这里我们只需要在loop body中加入arguments变量,就可以阻止string type check opcode的hoist.构造完有问题的循环体后,我们在循环体的前后加入两个数组的access,在循环体的callback中改变数组的类型,导致type confusion.<br>
最后JIT的函数体如下:<br>[![](https://blogs.projectmoon.pw/2018/10/26/Chakra-JIT-Loop-LandingPad-ImplicitCall-Bypass/7.png)](https://blogs.projectmoon.pw/2018/10/26/Chakra-JIT-Loop-LandingPad-ImplicitCall-Bypass/7.png)<br>
给JIT profile的时候,我们传入一个string类型给string 参数:<br>[![](https://blogs.projectmoon.pw/2018/10/26/Chakra-JIT-Loop-LandingPad-ImplicitCall-Bypass/8.png)](https://blogs.projectmoon.pw/2018/10/26/Chakra-JIT-Loop-LandingPad-ImplicitCall-Bypass/8.png)<br>
这里传入一个带回调的obj触发漏洞,这里需要注意的是我们不能进入循环体,不然slice函数的string type check会失败然后bailout,所以start和end都必须为0,但是无论进不进入循环体,LandingPad的指令(回调函数)都是会执行的:<br>[![](https://blogs.projectmoon.pw/2018/10/26/Chakra-JIT-Loop-LandingPad-ImplicitCall-Bypass/9.png)](https://blogs.projectmoon.pw/2018/10/26/Chakra-JIT-Loop-LandingPad-ImplicitCall-Bypass/9.png)<br>
这个特性同时也会产生一些JS层面上的bug,同一段代码在edge中会触发回调,在其他主流浏览器中不会触发回调(事实也不应该触发回调,毕竟我们没有进入循环体,没有执行|let tmp2 = string + ‘projectmoon’ + ‘projectmoon’;|语句).<br>
通过这个type confusion我们很容易泄露任何对象的地址和伪造任何对象(参考我们的第一篇文章),有了这两个原语,距离RCE就不远了,具体这里就不再叙述,网络上有大量的公开文章.



## 总结

我们可以看到,通过不同block之间的优化,我们可以得到一些比较复杂的bug,而这些bug往往隐藏得比较深,fuzz也比较难以得到.也启发了我们以后在审阅JIT的相关漏洞的时候,不要再单单针对某个opcode,而是通过block甚至function为单元的审核.

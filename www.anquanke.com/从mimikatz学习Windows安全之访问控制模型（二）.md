> 原文链接: https://www.anquanke.com//post/id/250365 


# 从mimikatz学习Windows安全之访问控制模型（二）


                                阅读量   
                                **27991**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t019dd4de7932e4e563.jpg)](https://p0.ssl.qhimg.com/t019dd4de7932e4e563.jpg)



作者：Loong716@[Amulab](https://github.com/Amulab)

## 0x00 前言

上次的文章分析了mimikatz的token模块，并简单介绍了windows访问控制模型的概念。在本篇文章中，主要介绍sid相关的概念，并介绍mimikatz的sid模块，着重分析sid::patch功能的原理。

上篇：[从mimikatz学习Windows安全之访问控制模型（一）](https://www.anquanke.com/post/id/249863)



## 0x01 SID简介

### <a class="reference-link" name="1.%20%E5%AE%89%E5%85%A8%E6%A0%87%E8%AF%86%E7%AC%A6(SID)"></a>1. 安全标识符(SID)

在Windows操作系统中，系统使用安全标识符来唯一标识系统中执行各种动作的实体，每个用户有SID，计算机、用户组和服务同样也有SID，并且这些SID互不相同，这样才能保证所标识实体的唯一性

SID一般由以下组成：
<li>
**“S”**表示SID，SID始终以S开头</li>
<li>
**“1”**表示版本，该值始终为1</li>
<li>
**“5”**表示Windows安全权威机构</li>
<li>
**“21-1463437245-1224812800-863842198”**是子机构值，通常用来表示并区分域</li>
<li>
**“1128”**为相对标识符(RID)，如域管理员组的RID为512</li>
[![](https://p2.ssl.qhimg.com/t019b6c4ddbe0ebb052.png)](https://p2.ssl.qhimg.com/t019b6c4ddbe0ebb052.png)

Windows也定义了一些内置的本地SID和域SID来表示一些常见的组或身份

<th style="text-align: left;">SID</th><th style="text-align: right;">Name</th>
|------
<td style="text-align: left;">S-1-1-0</td><td style="text-align: right;">World</td>
<td style="text-align: left;">S-1-3-0</td><td style="text-align: right;">Creator Owner</td>
<td style="text-align: left;">S-1-5-18</td><td style="text-align: right;">Local SYSTEM</td>
<td style="text-align: left;">S-1-5-11</td><td style="text-align: right;">Authenticated Users</td>
<td style="text-align: left;">S-1-5-7</td><td style="text-align: right;">Anonymous</td>

### <a class="reference-link" name="2.%20AD%E5%9F%9F%E4%B8%AD%E7%9A%84SID"></a>2. AD域中的SID

在AD域中，SID同样用来唯一标识一个对象，在LDAP中对应的属性名称为`objectSid`：

[![](https://p5.ssl.qhimg.com/t010264f45344372b1a.png)](https://p5.ssl.qhimg.com/t010264f45344372b1a.png)

重点需要了解的是LDAP上的`sIDHistory`属性

#### <a class="reference-link" name="(1)%20SIDHistory"></a>(1) SIDHistory

SIDHistory是一个为支持域迁移方案而设置的属性，当一个对象从一个域迁移到另一个域时，会在新域创建一个新的SID作为该对象的`objectSid`，在之前域中的SID会添加到该对象的`sIDHistory`属性中，此时该对象将保留在原来域的SID对应的访问权限

比如此时域A有一个用户User1，其LDAP上的属性如下：

<th style="text-align: left;">cn</th><th style="text-align: left;">objectSid</th><th style="text-align: left;">sIDHistory</th>
|------
<td style="text-align: left;">User1</td><td style="text-align: left;">S-1-5-21-3464518600-3836984554-627238718-2103</td><td style="text-align: left;">null</td>

此时我们将用户User1从域A迁移到域B，那么他的LDAP属性将变为：

<th style="text-align: left;">cn</th><th style="text-align: left;">objectSid</th><th style="text-align: left;">sIDHistory</th>
|------
<td style="text-align: left;">User1</td><td style="text-align: left;">S-1-5-21-549713754-3312163066-842615589-2235</td><td style="text-align: left;">S-1-5-21-3464518600-3836984554-627238718-2103</td>

此时当User1访问域A中的资源时，系统会将目标资源的DACL与User1的`sIDHistory`进行匹配，也就是说User1仍具有原SID在域A的访问权限

值得注意的是，该属性不仅在两个域之间起作用，它同样也可以用于单个域中，比如实战中我们将一个用户A的`sIDHistory`属性设置为域管的`objectSid`，那么该用户就具有域管的权限

另一个实战中常用的利用，是在金票中添加Enterprise Admins组的SID作为`sIDHistory`，从而实现同一域林下的跨域操作，这个将在后面关于金票的文章中阐述

#### <a class="reference-link" name="(2)%20SID%20Filtering"></a>(2) SID Filtering

SID Filtering简单的说就是跨林访问时目标域返回给你的服务票据中，会过滤掉非目标林中的SID，即使你添加了`sIDHistory`属性。SID Filtering林信任中默认开启，在单林中默认关闭

具体可以参考微软的文档和[@dirkjanm](https://github.com/dirkjanm)的文章：

[https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-pac/55fc19f2-55ba-4251-8a6a-103dd7c66280?redirectedfrom=MSDN](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-pac/55fc19f2-55ba-4251-8a6a-103dd7c66280?redirectedfrom=MSDN)

[https://dirkjanm.io/active-directory-forest-trusts-part-one-how-does-sid-filtering-work/](https://dirkjanm.io/active-directory-forest-trusts-part-one-how-does-sid-filtering-work/)



## 0x02 mimikatz的sid模块

### <a class="reference-link" name="1.%20sid::lookup"></a>1. sid::lookup

该功能实现SID与对象名之间的相互转换，有三个参数：
<li>
**/name**：指定对象名，将其转换为SID</li>
<li>
**/sid**：指定SID，将其转换为对象名</li>
<li>
**/system**：指定查询的目标计算机</li>
[![](https://p0.ssl.qhimg.com/t01feb4cf691859af67.png)](https://p0.ssl.qhimg.com/t01feb4cf691859af67.png)

### <a class="reference-link" name="2.%20sid::query"></a>2. sid::query

该功能支持通过SID或对象名来查询对象的信息，同样有三个参数，使用时指定**/sam**或**/sid**，**/system**可选
<li>
**/sam**：指定要查询对象的`sAMAccountName`
</li>
<li>
**/sid**：指定要查询对象的`objectSid`
</li>
<li>
**/system**：指定查询的目标域控（LDAP）</li>
[![](https://p0.ssl.qhimg.com/t0196daaf81eda3e2f2.png)](https://p0.ssl.qhimg.com/t0196daaf81eda3e2f2.png)

这个功能其原理就是直接使用LDAP查询，通过`sAMAccountName`查询对应的`objectSid`，或者通过`objectSid`查询对应的`sAMAccountName`

其核心是调用Windows一系列的LDAP操作API，主要是`ldap_search_s()`：

[![](https://p3.ssl.qhimg.com/t01cfa0d2116dddc2fe.png)](https://p3.ssl.qhimg.com/t01cfa0d2116dddc2fe.png)

### <a class="reference-link" name="3.%20sid::modify"></a>3. sid::modify

该功能用于修改一个域对象的SID，可以使用的参数有三个：
<li>
**/sam**：通过`sAMAccountName`指定要修改SID的对象</li>
<li>
**/sid**：通过`objectSid`指定要修改SID的对象</li>
<li>
**/new**：要修改对象的新SID</li>
使用该功能是需要先使用sid::patch功能对**xxxx**进行patch（自然也需要先开启debug特权），需要在域控上执行

[![](https://p3.ssl.qhimg.com/t01e658cc762e81eba4.png)](https://p3.ssl.qhimg.com/t01e658cc762e81eba4.png)

修改时的操作就很简单了，调用LDAP操作的API对域对象的`objectSid`进行修改，主要使用的是`ldap_modify_s()`：

[![](https://p2.ssl.qhimg.com/t01af925af50276fca3.png)](https://p2.ssl.qhimg.com/t01af925af50276fca3.png)

### <a class="reference-link" name="4.%20sid::add"></a>4. sid::add

该功能用来向一个域对象添加`sIDHistoy`属性，有两个参数：
<li>
**/sam**：通过`sAMAccountName`指定要修改的对象</li>
<li>
**/sid**：通过`objectSid`指定要修改的对象</li>
<li>
**/new**：要修改`sIDHistory`为哪个对象的SID，该参数可指定目标的`sAMAccountName`或`objectSid`，当指定名称时会先调用`LookupAccountSid`将其转换为SID</li>
使用该功能也要先执行sid::patch，修改时同样是操作LDAP通过`ldap_modify_s()`修改，不再赘述

[![](https://p0.ssl.qhimg.com/t01d3d9801d599032ce.png)](https://p0.ssl.qhimg.com/t01d3d9801d599032ce.png)

### <a class="reference-link" name="5.%20sid::clear"></a>5. sid::clear

该功能用来清空一个对象的`sIDHistory`属性
<li>
**/sam**：要清空`sIDHistory`的对象的`sAMAccountName`
</li>
<li>
**/sid**：要清空`sIDHistory`的对象的`objectSid`
</li>
[![](https://p4.ssl.qhimg.com/t01c039760878566b0a.png)](https://p4.ssl.qhimg.com/t01c039760878566b0a.png)

原理就是使用`ldap_modify_s()`将目标对象`sIDHistory`属性修改为空

### <a class="reference-link" name="6.%20sid::patch"></a>6. sid::patch

对域控LDAP修改过程中的验证函数进行patch，需要在域控上执行，该功能没有参数

patch共分为两个步骤，如果仅第一步patch成功的话，那么可以使用sid::add功能，两步都patch成功的话才可以使用sid::modify功能

[![](https://p2.ssl.qhimg.com/t017b5b6a1fd0a4a89f.png)](https://p2.ssl.qhimg.com/t017b5b6a1fd0a4a89f.png)



## 0x03 sid::patch分析

sid::patch在系统版本 &lt; Vista时，patch的是samss服务中ntdsa.dll的内存，更高版本patch的是ntds服务中ntdsai.dll的内存

[![](https://p5.ssl.qhimg.com/t01a708db9dfa8671a6.png)](https://p5.ssl.qhimg.com/t01a708db9dfa8671a6.png)

整个patch过程分为两步：
1. 第一步patch的是`SampModifyLoopbackCheck()`的内存
1. 第二步patch的是`ModSetAttsHelperPreProcess()`的内存
[![](https://p1.ssl.qhimg.com/t017d9aa8f59686d630.png)](https://p1.ssl.qhimg.com/t017d9aa8f59686d630.png)

我们以Windows Server 2012 R2环境为例来分析，首先我们需要找到NTDS服务所对应的进程，我们打开任务管理器选中NTDS服务，单击右键，选择“转到详细信息”就会跳转到对应进程，这里NTDS服务对应的进程是lsass.exe

[![](https://p2.ssl.qhimg.com/t0173153b6bacb0fe97.png)](https://p2.ssl.qhimg.com/t0173153b6bacb0fe97.png)

### <a class="reference-link" name="1.%20%E5%9F%9F%E6%8E%A7%E5%AF%B9LDAP%E8%AF%B7%E6%B1%82%E7%9A%84%E5%A4%84%E7%90%86"></a>1. 域控对LDAP请求的处理

大致分析一下域控对本地LDAP修改请求的过滤与处理流程，当我们修改`objectSid`和`sIDHistory`时，`SampModifyLoopbackCheck()`会过滤我们的请求，即使绕过该函数修改`objectSid`时，仍会受到`SysModReservedAtt()`的限制

侵入式切换到lsass进程并重新加载用户态符号表：

[![](https://p4.ssl.qhimg.com/t017acb9dc989037288.png)](https://p4.ssl.qhimg.com/t017acb9dc989037288.png)

给两个检查函数打断点

[![](https://p5.ssl.qhimg.com/t018234323ae7271cfb.png)](https://p5.ssl.qhimg.com/t018234323ae7271cfb.png)

此时我们修改一个用户的描述来触发LDAP修改请求

[![](https://p2.ssl.qhimg.com/t016834eb495d6f5123.png)](https://p2.ssl.qhimg.com/t016834eb495d6f5123.png)

命中断点后的调用栈如下：

[![](https://p2.ssl.qhimg.com/t018fc6cfc8f8894494.png)](https://p2.ssl.qhimg.com/t018fc6cfc8f8894494.png)

`SampModifyLoopbackCheck()`函数中存在大量Check函数，通过动态调试发现修改`sIDHistoy`的请求经过该函数后便会进入返回错误代码的流程

[![](https://p5.ssl.qhimg.com/t01b76b14c687fdd541.png)](https://p5.ssl.qhimg.com/t01b76b14c687fdd541.png)

继续调试到下一个断点

[![](https://p3.ssl.qhimg.com/t0116e3f09c6c11fe89.png)](https://p3.ssl.qhimg.com/t0116e3f09c6c11fe89.png)

在`SysModReservedAtt()`执行结束后，正常的修改请求不会在`jne`处跳转，而当修改`objectSid`时会在`jne`处跳转，进入返回错误的流程

[![](https://p4.ssl.qhimg.com/t01dfc8ff1983d4081b.png)](https://p4.ssl.qhimg.com/t01dfc8ff1983d4081b.png)

### <a class="reference-link" name="2.%20Patch%201/2"></a>2. Patch 1/2

当我们想要进行内存patch时，通常会寻找目标内存地址附近的一块内存的值作为标记，编写程序时首先在内存中搜索该标记并拿到标记的首地址，然后再根据偏移找到要patch的内存地址，然后再进行相应的修改操作

mimikatz正是使用这种方法，其在内存中搜索的标记在代码中有明确的体现：

[![](https://p5.ssl.qhimg.com/t017c7eafd7f89a569e.png)](https://p5.ssl.qhimg.com/t017c7eafd7f89a569e.png)

我们将域控的ntdsai.dll拿回本地分析，在其中搜索标记`41 be 01 00 00 00 45 89 34 24 83`

[![](https://p1.ssl.qhimg.com/t012c9d935876bfef1e.png)](https://p1.ssl.qhimg.com/t012c9d935876bfef1e.png)

这一部分内容是在函数`SampModifyLoopbackCheck()`函数的流程中，我们可以使用windbg本地调试对比一下patch前后的函数内容

首先我们找到lsass.exe的基址并切换到该进程上下文：

[![](https://p1.ssl.qhimg.com/t01b5b980a1015397ef.png)](https://p1.ssl.qhimg.com/t01b5b980a1015397ef.png)

使用`lm`列出模块，可以看到lsass进程中加载了ntdsai.dll，表明此时我们可以访问ntdsai.dll对应的内存了

[![](https://p4.ssl.qhimg.com/t01a34570be82391294.png)](https://p4.ssl.qhimg.com/t01a34570be82391294.png)

我们直接查看`SampModifyLoopbackCheck()`函数在内存中的反汇编

[![](https://p0.ssl.qhimg.com/t012d57c6fb082ad3eb.png)](https://p0.ssl.qhimg.com/t012d57c6fb082ad3eb.png)

为了对比patch前后的区别，我们使用mimikatz执行sid::patch，然后再查看函数的反汇编。如下图所示，箭头所指处原本是`74`也就是`je`，而patch后直接改为`eb`即`jmp`，使流程直接跳转到`0x7ffc403b2660`

[![](https://p5.ssl.qhimg.com/t0111bf5094d6ff2b2a.png)](https://p5.ssl.qhimg.com/t0111bf5094d6ff2b2a.png)

而`0x7ffc403b2660`处的代码之后基本没有条件检查的函数了，恢复堆栈和寄存器后就直接返回了，这样就达到了绕过检查逻辑的目的

### <a class="reference-link" name="3.%20Patch%202/2"></a>3. Patch 2/2

同理，按照mimikatz代码中的标记搜索第二次patch的位置`0f b7 8c 24 b8 00 00 00`

[![](https://p5.ssl.qhimg.com/t01e8d5a5c3ea17579f.png)](https://p5.ssl.qhimg.com/t01e8d5a5c3ea17579f.png)

查看`ModSetAttsHelperPreProcess()`处要patch的内存，patch前如下图所示

[![](https://p3.ssl.qhimg.com/t011b8768cc87a222f3.png)](https://p3.ssl.qhimg.com/t011b8768cc87a222f3.png)

patch完成后内存如下图，其实本质是让`SysModReservedAtt()`函数失效，在内存中寻找到标记后偏移-6个字节，然后将验证后的跳转逻辑`nop`掉

[![](https://p4.ssl.qhimg.com/t015af0a7ab2c65a1a5.png)](https://p4.ssl.qhimg.com/t015af0a7ab2c65a1a5.png)

### <a class="reference-link" name="4.%20%E8%A7%A3%E5%86%B3patch%E5%A4%B1%E8%B4%A5%E7%9A%84%E9%97%AE%E9%A2%98"></a>4. 解决patch失败的问题

由于mimikatz中内存搜索的标记覆盖的windows版本不全，所以经常会出现patch失败的问题。例如在我的Windows Server 2016上，第二步patch就会失败，这种情况多半是因为mimikatz中没有该系统版本对应的内存patch标记

[![](https://p2.ssl.qhimg.com/t019969c8b79c07cef1.png)](https://p2.ssl.qhimg.com/t019969c8b79c07cef1.png)

此时我们只需要将目标的ntdsai.dll拿下来找到目标地址

[![](https://p4.ssl.qhimg.com/t0197e11e5833f8ac22.png)](https://p4.ssl.qhimg.com/t0197e11e5833f8ac22.png)

然后修改为正确的内存标记和对应的偏移地址即可，如果新增的话记得定义好版本号等信息

[![](https://p3.ssl.qhimg.com/t01b73da5bffa8969c4.png)](https://p3.ssl.qhimg.com/t01b73da5bffa8969c4.png)

此时重新编译后就可以正常patch了

[![](https://p1.ssl.qhimg.com/t01957f0b750254b32e.png)](https://p1.ssl.qhimg.com/t01957f0b750254b32e.png)



## 0x04 渗透测试中的应用

在渗透测试中的利用，一个是使用SIDHistory属性来留后门，另一个是修改域对象的SID来实现域内的“影子账户”或者跨域等操作

### <a class="reference-link" name="1.%20SIDHistoy%E5%90%8E%E9%97%A8"></a>1. SIDHistoy后门

拿下域控后，我们将普通域用户test1的`sIDHistory`属性设置为域管的SID：

[![](https://p2.ssl.qhimg.com/t016167d7fa233532b0.png)](https://p2.ssl.qhimg.com/t016167d7fa233532b0.png)

此时test1将具有域管权限，我们可以利用这个特性来留后门

[![](https://p1.ssl.qhimg.com/t017b660d19dc67e6ff.png)](https://p1.ssl.qhimg.com/t017b660d19dc67e6ff.png)

### <a class="reference-link" name="2.%20%E5%9F%9F%E5%86%85%E2%80%9C%E5%BD%B1%E5%AD%90%E8%B4%A6%E6%88%B7%E2%80%9D"></a>2. 域内“影子账户”

假设我们此时拿到了域控，然后设置一个普通域用户的SID为域管的SID

[![](https://p3.ssl.qhimg.com/t0118a73048d8820e88.png)](https://p3.ssl.qhimg.com/t0118a73048d8820e88.png)

此时我们这个用户仍然只是Domain Users组中的普通域成员

[![](https://p2.ssl.qhimg.com/t019c2a2ade9e91e3d4.png)](https://p2.ssl.qhimg.com/t019c2a2ade9e91e3d4.png)

但该用户此时已经具有了域管的权限，例如dcsync：

并且此时也可以用该用户的账号和密码登录域控，登录成功后是administrator的session。但该操作很有可能造成域内一些访问冲突（猜测，未考证），建议在生产环境中慎用

### <a class="reference-link" name="3.%20%E8%B7%A8%E5%9F%9F"></a>3. 跨域

通常我们拿到一个域林下的一个子域，会通过黄金票据+SIDHistory的方式获取企业管理员权限，控制整个域林

除了这种方法，我们也可以直接修改当前子域对象的`sIDHistory`属性，假设我们现在拿到一个子域域控，通过信任关系发现存在一个父域，此时我们无法访问父域域控的CIFS

[![](https://p4.ssl.qhimg.com/t0108481a17320250b7.png)](https://p4.ssl.qhimg.com/t0108481a17320250b7.png)

但我们给子域域管的`sIDHistory`属性设置为父域域管的SID

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01559e76c3e104201b.png)

此时就可以访问父域域控的CIFS了：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0110c7c3de98ab4f21.png)



## 0x05 参考

[https://docs.microsoft.com/](https://docs.microsoft.com/)

[https://github.com/gentilkiwi/mimikatz](https://github.com/gentilkiwi/mimikatz)

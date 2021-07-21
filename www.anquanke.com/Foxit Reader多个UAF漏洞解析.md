> 原文链接: https://www.anquanke.com//post/id/161541 


# Foxit Reader多个UAF漏洞解析


                                阅读量   
                                **94023**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t01500b6acedb32e5d9.png)](https://p1.ssl.qhimg.com/t01500b6acedb32e5d9.png)

作者：ManchurianClassmate

## 0x00 简介

9月28号著名PDF阅读器厂商福昕针对Foxit Reader和Foxit PhantomPDF发布了例行安全更新，在其安全公告上涉及了其中一个包含较多CVE编号的修补，Foxit对此修补的描述为：“Addressed potential issues where the application could be exposed to Use-After-Free Remote Code Execution or Out-of-Bounds Read Information Disclosure vulnerability and crash. This occurs when executing certain JavaScript due to the use of document and its auxiliary objects which have been closed after calling closeDoc function”。本文就简单说一下该系列漏洞。



## 0x01 第一次报告

关于这个攻击面的发现在Foxit Reader之前的例行安全更新中修补的远程命令执行漏洞CVE-2018-3924和CVE-2018-3939。这两个漏洞由Cisco Talos的Aleksandar Nikolic提交，在7月19号被修补，有意思的是在8月16号Foxit又发布更新修补了CVE-2018-3924和CVE-2018-3939，明显第一次修补存在一些问题。

这两个漏洞的详情可以在Talos的博客上看到：[https://www.talosintelligence.com/vulnerability_reports/TALOS-2018-0588；https://www.talosintelligence.com/vulnerability_reports/TALOS-2018-0606](https://www.talosintelligence.com/vulnerability_reports/TALOS-2018-0588%EF%BC%9Bhttps:/www.talosintelligence.com/vulnerability_reports/TALOS-2018-0606)。



## 0x02 CVE-2018-3924

PDF格式是允许嵌入JavaScript脚本的，从而可以在文档中实现更丰富的功能，比如动态修改文档内容，自动发送电子邮件等。而这一切需要由PDF阅读器提供的JavaScript引擎以及一系列内置函数的支持。触发崩溃的PoC如下：

```
var v1 = new Array();

function main() `{`

v1.toString = f;

app.activeDocs[0].mailForm(`{``}`,v1,`{``}`,`{``}`,`{``}`,true,`{``}`);

`}`

function f() `{`

app.activeDocs[0].closeDoc();

    return 1;

`}`
```

该漏洞出在JavaScript内置类型Doc的mailForm()方法中，Doc类型是Adobe Acrobat API中定义的用于访问PDF文档的内置类，为了和Adobe Acrobat兼容，Foxit Reader也实现了Adobe Acrobat API中的绝大多数内容。全局变量app属于App类型，其方法activeDocs()用于返回当前活跃的文档的Doc实例，Doc的另外一个方法closeDoc()用于关闭文档并从内存中销毁相应的对象。Adobe Acrobat API文档中没有限制mailForm()参数的类型，但可以参考开源的PDFium的代码：

[![](https://p3.ssl.qhimg.com/t01380f8bce5032bd54.png)](https://p3.ssl.qhimg.com/t01380f8bce5032bd54.png)

第二个参数在存在的情况下会被强制转化为字符串类型，结合PoC可以推知转化的过程会调用v1.prototype.toString()，而这个函数被赋值为f()，运行时会销毁当前Doc对象，而销毁后某些代码又会继续引用Doc对象中的属性，从而形成UAF漏洞。实际运行时情况也的确如此，程序会崩溃在0x00B8D5C9的位置上（9.0.1.1049版本）：

[![](https://p3.ssl.qhimg.com/t0132252a4b8bfd37fd.png)](https://p3.ssl.qhimg.com/t0132252a4b8bfd37fd.png)

edi中存储着当前Doc对象的指针，这里程序调用了Doc对象内部0x5C偏移处的另一个对象的一个虚函数，因为该虚表指针早已被销毁并填充进了其他数据，从而触发Access violation崩溃。从测试情况来看，可以很容易的控制并填充Doc对象的内存区域，从而控制eip，实现任意代码执行。



## 0x03 CVE-2018-3939

这次的崩溃PoC和CVE-2018-3924长得很像：

```
function main() `{`

var a = `{``}`;

a.toString =  f;

app.activeDocs[0].createTemplate(false,a);

`}`


function f() `{`

app.activeDocs[0].closeDoc();

`}`


main();
```

明显可以看出问题很类似，只不过有漏洞的代码在另一个函数里面罢了。运行后崩溃的位置也很相似：

[![](https://p3.ssl.qhimg.com/t01bc88a398f3f41598.png)](https://p3.ssl.qhimg.com/t01bc88a398f3f41598.png)

又是通过调用Doc对象偏移0x5C的对象的虚函数来触发UAF。



## 0x04 修补

修补后的9.2.0.9297版本中这两个函数几乎都被重写了但从createTemplate()函数的新版本中可以看到在转换类型前对参数类型进行了检查，如果是Object类型则不做类型转换，从而避免执行toString()方法：

[![](https://p5.ssl.qhimg.com/t01e8f60589f7b9fa45.png)](https://p5.ssl.qhimg.com/t01e8f60589f7b9fa45.png)

也就是说按福昕的理解，问题出在参数类型过滤不严。



## 0x05 后续

CVE-2018-3924和CVE-2018-3939的情况明显不会是个例，于是就有了这次较多的同类问题的报告。这里有一个额外的小问题，现在网上可以找到的Adobe Acrobat API文档是2007年的，而后续版本的API又有了一些增补，关于这些变化至少本人没有找到公开的文档。所以这波报告涉及了一些2007年文档中没有的API函数。实际去看这些后续增加的API时会发现有相当一部分函数Foxit Reader都只是做了一个空壳子，里面没有任何代码实现。可能这一部分功能福昕并不重视。后续发现有该问题的函数还有Doc类的mailDoc()方法、createIcon()方法、getPageBox()方法、gotoNamedDest()方法、importAnFDF()方法等等。

关于利用效果，在做了简单的堆喷射后在关闭DEP的环境中可以弹出计算器：

[![](https://p2.ssl.qhimg.com/t014ec2eb3d0f7a51a7.gif)](https://p2.ssl.qhimg.com/t014ec2eb3d0f7a51a7.gif)

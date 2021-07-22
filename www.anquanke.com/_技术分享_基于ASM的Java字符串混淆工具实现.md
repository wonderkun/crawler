> 原文链接: https://www.anquanke.com//post/id/86941 


# 【技术分享】基于ASM的Java字符串混淆工具实现


                                阅读量   
                                **159813**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t01d5fb3a1749ce1553.png)](https://p1.ssl.qhimg.com/t01d5fb3a1749ce1553.png)



**0x0 前言**

****提到字符串混淆，就要解释下为什么要做字符串混淆，之前文章有介绍过基于smali的字符串混淆，但基于smali就必须先反编译，使用成本太大，而混淆往往用于开发层面，目前Android开发的主流语言还是**Java**（kotlin），使用**NDK**开发的偏少，如果编译时不进行处理，那么使用一些反编译工具反编译后就相当于在阅读源码，市面上主流的proguard混淆工具并没有提供**字符串混淆**功能，而其它混淆工具如DashO，Zelix，DexGuard，Allatori等等均属于收费工具，做字符串混淆的初衷主要是为了提高逆向门槛，或是从另一方面减少硬编码的危害。<br>

**<br>**

**0x1 介绍**

看一例简单字符串混淆，如下示例：

[![](https://p4.ssl.qhimg.com/t01097482bc37383868.webp)](https://p4.ssl.qhimg.com/t01097482bc37383868.webp)

对于对称算法来说，泄漏密钥则意味数据包可被篡改（此处未考虑数据包做了完整性校验），站在逆向的角度来说，对于数据包的逆向分析一般会从url地址、参数类型、猜测加密类型、堆栈跟踪等多个方面去寻找加解密方法，而前三种方式是用的较多的，比如http://helloworld.com/keyword=d3Fld3FlMTExc2QuLg==,反编译后则可以通过搜索**keyword关键字**去查找值内容的加密，亦或是通过猜测加密类型，如上述值内容其实仅做了个base64编码，在尝试解码后就可以拿到明文，当如果解码后依然是密文，一方面就可以通过查找函数引用，而我自己使用的方式直接去靠猜（= =），常规的加密方式无非是**AES**，**DES**，**RSA**（这三种是用的最多的），此处考虑的是加解密算法在Java层实现，较大型的app一般已经使用openssl在jni层实现了，这里不做讨论，通过搜索AES，DES，RSA关键字再稍加分析一般就可以找到真正的加解密函数。

字符串混淆就是为了增大直接搜索关键字的难度，逆向人员在遇到字符串混下后首先要解决的就是反混淆，可通过静态反混淆或是动态代码插桩查看明文，此处针对一项简单的字符串混淆介绍下反混淆。

[![](https://p3.ssl.qhimg.com/t01d31d6817796c6e08.png)](https://p3.ssl.qhimg.com/t01d31d6817796c6e08.png)

这里每次会调用a类中的c方法对加密字符串进行解密，这里有两种还原方式，一种是借助jeb写脚本遍历c方法的引用进行还原，但不是永久性还原，另一种就是基于smali做反混淆，将app反编译smali后，上图的代码如下<br>

[![](https://p4.ssl.qhimg.com/t018bb51e73eaa358ac.png)](https://p4.ssl.qhimg.com/t018bb51e73eaa358ac.png)

可以看到在声明了一个const-string后紧接着就是解密方法，根据这个特性，写个方法遍历下所有包含这个特性的字符串进行还原然后编码回去即可，需要注意的就是smali里中文显示的是unicode形式。

**<br>**

**0x2 实现**

那么在处理过字符串后以字符串的形式编码是不可靠的，静态还原难度太低，于是有了以数组形式展现的方式，目前效果如下：

[![](https://p5.ssl.qhimg.com/t017832dc2b284350e7.png)](https://p5.ssl.qhimg.com/t017832dc2b284350e7.png)

展示过效果图接下来就是介绍原理，本工具是基于[StringFog](https://github.com/MegatronKing/StringFog)进行的二次开发，无论是gradle插件还是jar包混淆，处理的对象都是class字节码，那这里就引用了著名的asm字节码工具，遍历每个class文件，通过重写ClassVisitor中的visitField、visitMethod、visitEnd方法，对于全局变量，需要考虑它的修饰符是否为static和final，在visitField时根据其不同的修饰区分出三种情形：

```
((access .) (access .) ) `{`
    .add(ClassStringField(name, () value));
    value ;
`}`
((access .) (access .) ) `{`
    .add(ClassStringField(name, () value));
    value ;
`}`
((access .) (access .) ) `{`
    .add(ClassStringField(name, () value));
    value ;
`}`
```

此处用于拿到Field的名称和值用于后面的加密，而在visitMethod时，需要对（static块），（构造方法）和普通方法进行分别判断，同时对上面获取到的变量进行判断，对非空值变量进行加密，对于方法内部的字符串在visitLdcInsn时进行判断是否为String类型和值是否为空，非空则进行加密，以下代码限于篇幅省略了一部分。

```
(.equals(name)) `{`
        ...
    (ClassStringField mStaticFinalFields) `{`
        (.value ) `{`
            ;
        `}`
        startEncode(.mv, .value);
        ...
        visitLdcInsn(cst) `{`
            (cst cst TextUtils.isEmptyAfterTrim(() cst)) `{`
                lastStashCst () cst;
                startEncode(.mv, lastStashCst);
            `}`
        `}`
        visitFieldInsn(, String owner, name, desc) `{`
            (mClassName.equals(owner) lastStashCst ) `{`
                ;
                (ClassStringField mStaticFields) `{`
                    (.name.equals(name)) `{`
                        ;
                        ;
                    `}`
          ...
                `}`
            `}`;
        `}` (.equals(name)) `{`
            mv MethodVisitor(Opcodes.ASM5, mv) `{`
                (cst) `{`
                    (cst cst TextUtils.isEmptyAfterTrim(() cst)) `{`
                        startEncode(.mv, () cst);
                    `}`
                `}`
            `}`;
        `}`
```

而真正的加密重点即在startEncode方法

```
private void startEncode(MethodVisitor mv, String str) `{`
    boolean special = false;
    char[] charArray = str.toCharArray();
    int len = charArray.length;
    if (len &lt;= 0) `{`
        return;
    `}`
    for (char c : charArray) `{`
        if (c &gt; 255) `{`
            special = true;
            break;
        `}`
    `}`
    if (special) `{`
        encode3(mv, str);
    `}` else `{`
        encode2(mv, str);
    `}`
`}`
```

这里做了个判断，当char值大于255时，进行了另一种混淆，原因在于使用的自定义混淆算法根据c版本翻译而来，c版本类型为unsigned char 在实验过程中碰到了很多的问题，即当出现中文字符或者其它特殊字符时，造成运行崩溃或是乱码，故当遇到大于255的字符时，则使用常规的异或进行处理

```
;
(str, key) `{`
    [] ;
    `{`
        str.getBytes();
    `}` (e) `{`
        str.getBytes();
    `}`
    .;
    key.length();
    (; ; ) `{`
        [] () ([] key.charAt());
    `}`
    StringBuilder(.);
    () `{`
        .append(.charAt(() ));
        .append(.charAt(() ));
    `}`
    .toString();
    ;
`}`
```

为避免出现乱码问题，在将string转为byte时优先指定utf-8编码，而针对0-255的范围则使用的自定义加密方式，下面看一个c版本的简单自定义解密方法

```
[] =
        `{`
                `}`(= &lt; ()++) `{`
    = []= (&gt;&gt; ) | (&lt;&lt; )-= = ~-= ^= [] = `}`
()
```

运行后显示ysrc。

不过仅有解密方法，如何生成加密方法呢？这就需要我们自己进行逆推，其中取反，加减乘除异或都不存在难度，唯一需要注意的就是一个移位运算，翻译成java后需要对每次移位后的结果&amp;0xff，防止越界，逆推后的java代码如下：

```
(ch) `{`
    () (ch );
`}`
(str) `{`
    [] str.toCharArray();
    .;
    (; ; ) `{`
        ([]);
        (() ());
        ();
        ();
        ();
        ();
        [] ();
    `}`
`}`
```

由于java中没有unsigned char 这种类型，所以需要保证每次计算后的结果都在0-255以内。

有了加密方式就可以对字符串进行加密了，在使用asm时也碰到了不少问题，借助class字节码分析工具也成功解决了这些问题，如下为针对char[]的加密方式

```
(mv, str) `{`
    .().toString().replace(, ).trim().substring(, );
    [] .(str, );
    .;
    mv.visitIntInsn(., );
    mv.visitIntInsn(., .);
    (; ; ) `{`
        mv.visitInsn(.);
        mv.visitIntInsn(., );
        mv.visitIntInsn(., []);
        mv.visitInsn(.);
    `}`
    mv.visitLdcInsn(() );
    mv.visitMethodInsn(., , , , );
`}`
```

上述代码中使用一个randomUUID生成一个随机异或因子用于对字符的异或，在调用加密方法后使用asm填充到class文件中，根据字节码生成数组的结构

**声明数组大小**

**声明数组类型**

**第0个**

**第0个字符**

**保存**

**第1个**

**第1个字符**

**保存**

这里使用for循环将所有字符填充进去后再声明调用方法即完成了字符串加密，这里有个坑就是在添加数组时可能导致堆栈不平衡，可以通过手动去修正但asm也为我们考虑到了这一点可以让程序自动帮我们进行计算，只需要在new ClassWriter(int)时传入1即可，具体细节可以参见asm文档：<br>

[![](https://p1.ssl.qhimg.com/t01b9929d7f5af332b3.webp)](https://p1.ssl.qhimg.com/t01b9929d7f5af332b3.webp)

完成了以上所有的加密工作后就需要封装成一键工具来使用，这里介绍下gradle的使用方式，在build.gradle中添加如下代码



```
.libraryVariants.allvariant -&gt;
    variant.javaCompile.doLast$variant.javaCompile.destinationDirmain ;
            args ,
                    .,
                    variant.javaCompile.destinationDir
```

如果是module模块，则需要修改applicationVariants为libraryVariants，其中的javaCompile.destinationDir指向目录为buildintermediatesclassesdebug,正式版指向的是release，里面包含了当前已经编译的class文件，那混淆思路即为：遍历所有class文件-&gt;忽略白名单文件-&gt;混淆class文件，生成重命名文件-&gt;删除原始文件-&gt;重命名为原始文件名。

**<br>**

**0x3 总结**

asm是一款非常强大的class字节码框架，但学习难度也很高（个人觉得），一部分的混淆工具也是基于asm开发的，包括强大的jadx反编译套件也是基于asm，使用好asm可以帮助我们解决很多难以手工解决的技术问题。

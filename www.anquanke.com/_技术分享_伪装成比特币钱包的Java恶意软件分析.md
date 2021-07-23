> 原文链接: https://www.anquanke.com//post/id/85461 


# 【技术分享】伪装成比特币钱包的Java恶意软件分析


                                阅读量   
                                **93345**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：malwarebytes.com
                                <br>原文地址：[https://blog.malwarebytes.com/cybercrime/2017/01/from-a-fake-wallet-to-a-java-rat/](https://blog.malwarebytes.com/cybercrime/2017/01/from-a-fake-wallet-to-a-java-rat/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t013f38da5ec6408931.jpg)](https://p2.ssl.qhimg.com/t013f38da5ec6408931.jpg)

<br>

****

翻译：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：200RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿

**<br>**

**一、概要**

近期，研究人员发现了一款恶意软件，该软件采用钓鱼邮件方式进行传播，邮件主题是经过伪装的比特币钱包。当用户点击恶意链接后会下载Dropbox网盘上的一个名为"wallet.aes.json.jar"的jar文件，该文件实际上是一个远控工具（RAT，Remote Access Tool）并经过了多重混淆加密，本文对该恶意软件进行了细致分析。

<br>

**二、样本摘要**

Dropbox上的样本链接（当前已失效）：

[https://www.dropbox.com/s/sl8ton6reobdyb7/wallet.aes.json.zip?dl=1](https://www.dropbox.com/s/sl8ton6reobdyb7/wallet.aes.json.zip?dl=1)

涉及到的样本文件及virustotal链接信息：

[851bc674d181910870fbba24763d5348](https://virustotal.com/en/file/1a808bda96bedb9f456430a4a6538e1d41dd5564ad1cde40958fe1d0f4e4fd1c/analysis/) – 初始文件(wallet.aes.json.jar)

    [2eb123e43971eb2eaf437eaeffeeed8e](https://virustotal.com/en/file/eeb22a819578859c803513af690343842d90291377d18018ada025ebefde799b/analysis/1484104595/) – 第二阶段主文件

        [24840e382da8d1709647ee18e33b63f9](https://virustotal.com/en/file/61b740df9a604a791188497d705ef530625075670acc4bbc335c014ed4f40514/analysis/1484166467/) – 第三阶段主文件

            JAR包中附带的DLL文件：

                        [0ad1fc3ddb524c21c9b31cbe3fd57780](https://virustotal.com/en/file/7da7e2e66b5b79123f9d731d60be76787b6374681e614099f18571a4c4463798/analysis/) – keyamd64.dll

                        [0b7b52302c8c5df59d960dd97e3abdaf](https://virustotal.com/en/file/a6be5be2d16a24430c795faa7ab7cc7826ed24d6d4bc74ad33da5c2ed0c793d0/analysis/) – keyx86.dll

                        [9e0b34a35296b264d4b0739da3b63387](https://virustotal.com/en/file/2ed9d4a04019f93fd80213aae9274ea6c0b043469c43cf30759dd19df3c4e0a0/analysis/) – protectoramd64.dll

                        [c17b03d5a1f0dc6581344fd3d67d7be1](https://virustotal.com/en/file/1afb6ab4b5be19d0197bcb76c3b150153955ae569cfe18b8e40b74b97ccd9c3d/analysis/) – protectorx86.dll

        行为分析中释放的文件：      

        [7f97f5f336944d427c03cc730c636b8f](https://virustotal.com/en/file/9613caed306e9a267c62c56506985ef99ea2bee6e11afc185b8133dda37cbc57/analysis/) – .reg

        [0b7b52302c8c5df59d960dd97e3abdaf](https://virustotal.com/en/file/a6be5be2d16a24430c795faa7ab7cc7826ed24d6d4bc74ad33da5c2ed0c793d0/analysis/) – DLL 

<br>

**三、行为分析 **

启动后该恶意软件在后台静默运行，使用Process Explorer可以发现该软件启动后会部署并运行某些脚本文件。

[![](https://p5.ssl.qhimg.com/t014dad91a95ac7390f.png)](https://p5.ssl.qhimg.com/t014dad91a95ac7390f.png)

具体来说，该恶意软件运行后会将一些文件释放到%TEMP%目录中，这些文件包括vbs脚本、reg注册表文件以及一个DLL文件。

[![](https://p1.ssl.qhimg.com/t01f6b07c7259244915.png)](https://p1.ssl.qhimg.com/t01f6b07c7259244915.png)

vbs脚本用来检测本机所安装的安全软件信息（防病毒软件、防火墙），运行完毕后脚本被迅速删除。捕获的脚本片段如下所示。

```
Set oWMI = GetObject("winmgmts:`{`impersonationLevel=impersonate`}`!\.rootSecurityCenter2")
Set colItems = oWMI.ExecQuery("Select * from FirewallProduct")
For Each objItem in colItems
    With objItem
        WScript.Echo  "`{`""FIREWALL"":""" &amp; .displayName &amp; """`}`"
    End With
Next
```

恶意软件作为一个隐藏文件安装在本地硬盘的一个隐藏目录中，去掉Windows的隐藏文件及文件夹选项后，我们就可以找到名为Windows.Windows的软件真身。

[![](https://p3.ssl.qhimg.com/t01982caea574e82ba4.png)](https://p3.ssl.qhimg.com/t01982caea574e82ba4.png)

恶意软件的本地持久化通过写入注册表键值来实现。

[![](https://p1.ssl.qhimg.com/t01210ced0ba0eb82da.png)](https://p1.ssl.qhimg.com/t01210ced0ba0eb82da.png)

电脑感染该软件的第一个表现就是UAC窗口的弹出，原因是恶意软件试图运行reg文件。如果用户允许该动作，系统将弹出另一个窗口通知用户UAC已被禁用。

随后恶意软件与远端服务器建立连接，服务器地址是104.239.166.119（jamoos88.ddns.net）。

[![](https://p0.ssl.qhimg.com/t01e11868060233eb35.png)](https://p0.ssl.qhimg.com/t01e11868060233eb35.png)

捕获的部分通信报文片段如下图所示。

[![](https://p0.ssl.qhimg.com/t01de7a30b5cfa43eb0.png)](https://p0.ssl.qhimg.com/t01de7a30b5cfa43eb0.png)

<br>

**四、代码分析**

恶意软件经过了高强度的混淆加密，共有三个jar文件彼此嵌套。两个内部jar文件采用强加密算法（RSA+AES）加密，最后一层（也就是第三层）是一个核心模块。

**（一）第一阶段**

借助JD-GUI等工具对恶意软件进行反编译，输出的结果仍是人工不可读的。通过对初步反编译得到的字符串进行分析，我们可知恶意软件使用了Allatori Obfuscator v6.0 DEMO进行混淆处理。

幸运的是，我们可以使用[免费的java去混淆工具](https://github.com/java-deobfuscator/deobfuscator)对恶意软件进行处理，所使用的命令为：

```
java -jar deobfuscator-1.0.0.jar -input wallet.aes.json.jar 
-output deobfuscated.jar 
-transformer general.SyntheticBridgeTransformer 
-path /usr/lib/jvm/java-8-openjdk-amd64/jre/lib/rt.jar
```

经过初步去混淆处理后，利用JD-GUI等其他反编译工具依然不能给出有效的输出代码。最后我们通过[CFR反编译器](http://www.benf.org/other/cfr/)设法得到了一个有效的输出代码。为了得到其他文件资源（如jar包里的文件资源），我们将jar包后缀名改为zip并将其解压。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t010170181e3217749e.png)

从Manifest文件信息中可知，恶意代码从MANAGER类开始执行。

[![](https://p3.ssl.qhimg.com/t0168f811d303212b6a.png)](https://p3.ssl.qhimg.com/t0168f811d303212b6a.png)

在主文件夹中，我们可以看到有其他几个使用混淆名称的类。主文件夹中包含了两个子文件夹，里面包含一些加密文件，以及两张相同的JPEG图片，图片如下图所示。

[![](https://p4.ssl.qhimg.com/t01c0c6d0ad4370e1fb.jpg)](https://p4.ssl.qhimg.com/t01c0c6d0ad4370e1fb.jpg)

图片的内容十分有趣，看上去像是一张驾驶执照照片，我们猜测恶意软件添加这张图片的目的是作为无用信息以进一步加深混淆。

为了得到可读的代码片段，我们仍然需要对去混淆处理后的代码做大量的手动分析清除工作，包括类名以及其他所有的字符串信息都需要做去混淆处理。经过处理后可知，类i中存储了混淆所用的路径及键值。

```
public final class i `{`
    public static String b = c.a(f.a("t'VdU:t/b;H,"));
    public static String a = c.a(f.a("J U`{`u0015$C'B @"T$Q'"));
`}`
```

经过手动去混淆后类i代码为：

```
public final class i `{`
    public static String key = "lks03oeldkfirowl";
    public static String path = "/lp/sq/d.png";
`}`
```

恶意软件使用了类c中封装的一个a方法进行解密。

```
byte []dec_content = c.a(input_data, key.getBytes());
```

对类c进行人工去混淆后，我们发现a方法的功能是进行AES加密。

```
public static byte[] a(byte[] a2, byte[] a3) `{`
    try `{`
        Key key = new SecretKeySpec((byte[])a3, "AES");
        Cipher cipher2 = Cipher.getInstance("AES/ECB/PKCS5Padding");
        cipher2.init(2, key);
        a2 = cipher2.doFinal(a2);
        return a2;
    `}`
    catch (Exception v1) `{`
        return null;
    `}`
`}`
```

文件解密后指向一个[xml文件](https://gist.github.com/hasherezade/4997bae081a9d62305e33a6f97725c60#file-d-png-xml)。

这个xml文件有很多垃圾字段，字段的作用是让整个内容更加难以阅读，唯一有用的两个字段如下图所示。

[![](https://p2.ssl.qhimg.com/t010e89c6ec3eb91430.png)](https://p2.ssl.qhimg.com/t010e89c6ec3eb91430.png)

SERVER字段指向了另一个加密文件，PASSWORD字段是一个AES密钥。

解密涉及到两个步骤，分别由两个类进行处理。首先是C类的AES算法，其次是B类的Gzip解压方法。

```
byte []dec_content = b.a(c.a(input_data, key.getBytes()));
```

经过上述操作后，我们得到了第二阶段所用的JAR文件。

完整的解密程序[在此](https://gist.github.com/hasherezade/e08e9eb1e40a5822bb1f6b0abd9c76e6)。

**（二）第二阶段**

与第一阶段类似，我们采用相同的去混淆工具清理了jar文件，将其解压后得到封装的文件资源，如下图所示。

[![](https://p4.ssl.qhimg.com/t019bbac313ac0fdfc6.png)](https://p4.ssl.qhimg.com/t019bbac313ac0fdfc6.png)

Jar的执行点是operational文件夹的JRat类，如下图所示。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01b36bfb6c465c86c9.png)

经过自动化去混淆处理后，所得[代码](https://gist.github.com/hasherezade/4997bae081a9d62305e33a6f97725c60#file-layer2-java)远远不能达到可读的程度。

经过人工对代码进行重构后，可知这段代码只是作为另一个加载器，用来解压并运行下一个阶段所用的jar包。

去混淆解密类代码如下：

```
package w;
import java.security.GeneralSecurityException;
import java.security.Key;
import java.security.interfaces.RSAPrivateKey;
import javax.crypto.Cipher;
import javax.crypto.spec.SecretKeySpec;
public class kyl `{`
    private byte[] encryptedAesKey;
    private byte[] encryptedBuffer;
    private static int mode = javax.crypto.Cipher.DECRYPT_MODE;
    public kyl() `{` `}`
    public void setEncryptedBuffer(byte[] value) `{`
        this.encryptedBuffer = value;
    `}`
    public void setEncryptedAesKey(byte[] value) `{`
        this.encryptedAesKey = value;
    `}`
    public byte[] decryptContent(Object object2) throws GeneralSecurityException `{`
        Cipher object = Cipher.getInstance("RSA");
        object.init(2, (RSAPrivateKey)object2);
        Cipher cipher2 = Cipher.getInstance("AES");
        byte []aesDecrypted = object.doFinal(this.encryptedAesKey);
        SecretKeySpec sKey = new SecretKeySpec(aesDecrypted, "AES");
        Cipher arrby = cipher2;
        arrby.init(mode, (Key)sKey);
        return arrby.doFinal(this.encryptedBuffer);
    `}`
`}`
```

完整的解密程序[在此](https://gist.github.com/hasherezade/fef5bd9b2b12d6bc384d40fc60213d05)。

Jar解压后的资源包括RSA私钥、加密的AES密钥以及加密后的内容。在对代码去混淆处理后，我们可以得到另一个XML文件。

[![](https://p3.ssl.qhimg.com/t012391025aa79fdf8b.png)](https://p3.ssl.qhimg.com/t012391025aa79fdf8b.png)

XML文件中每个属性都是一个指向其他资源的路径信息：

SERVER_PATH指向另一个加密的JAR文件，这个文件也是恶意软件的核心；

PASSWORD_CRYPTED是一个经过RSA加密的AES密钥；

PRIVATE_PASSWORD是一个RSA私钥。

使用同样的解密方法（RSA+AES）后，我们可以得到第三个JAR包。

**（三）第三阶段**

我们使用同样的自动化java去混淆器对代码进行清理，并对得到的jar文件进行反编译。

观察jar文件内部结构，我们可以找到一些熟悉元素，这些元素包括用于感染特定系统（windows, mac, linux）的功能函数，这也使我们进一步确信这就是恶意软件的核心。在key文件夹以及protect文件夹中，我们找到了释放到Windows系统%TEMP%目录下的DLL文件，同样也找到了一些负责SSL网络通信的类文件。

然而，去混淆处理是否成功很大程度上取决于我们所选择的反编译器。虽然JD-GUI非常擅长于呈现JAR包的内部结构，但它在所有类的反编译工作上却无能为力。我们可以轻松阅读其他没有被混淆的包，但RAT的核心（server包中的类）却是完全不可读的。

[![](https://p4.ssl.qhimg.com/t01f6a7eca847d7c79c.png)](https://p4.ssl.qhimg.com/t01f6a7eca847d7c79c.png)

另一个CFR反编译器给出了一个更好的[结果](https://gist.github.com/hasherezade/4997bae081a9d62305e33a6f97725c60#file-layer3-java)。

经过处理后我们最终得到了一些java代码，但去混淆工作还没结束。为了对抗分析，恶意软件使用了两种技术，首先，代码中的类、方法以及变量被重命名为无意义的字符串，其次，所有的字符串都经过了几个函数进行加密处理，并在运行时再解压使用。核心类中的大部分代码与下面这个代码片段类似。

[![](https://p0.ssl.qhimg.com/t01bd178bef2e82ed1b.png)](https://p0.ssl.qhimg.com/t01bd178bef2e82ed1b.png)

虽然有时我们在代码中能看到对某些可读名称的类的引用（如JSON解析器），但这类信息太少了，我们无法理解其背后的功能。对字符串的解码能够大幅度提升代码的可读性，但CFR中负责解码的函数输出并不理想。经过几次尝试后，我们最终选择了[Kraktau](https://github.com/Storyyeller/Krakatau)反编译器。

此外，代码中的函数使用所调用类的类名作为解密密钥，因此，如果我们试图在去混淆过程中对类进行重命名，我们将无法得到有效的字符串信息。

**（四）对配置文件进行解码**

在resources文件夹中，我们找到了三个有趣的文件：Key1.json，Key2.json以及config.json。

[![](https://p2.ssl.qhimg.com/t0147b66c8398aeac6b.png)](https://p2.ssl.qhimg.com/t0147b66c8398aeac6b.png)

这三个文件的加密方式与上一层加密方式相同：Key1是个经过序列化的RSA私钥，Key2是一个经过加密的AES密钥，config.json是一个经过AES加密的配置文件，相应的解密器代码可以在[这里](https://gist.github.com/hasherezade/fef5bd9b2b12d6bc384d40fc60213d05)找到。最终，我们得到了这个RAT的配置文件（[地址](https://gist.github.com/hasherezade/4997bae081a9d62305e33a6f97725c60#file-config-json)）。

从配置文件中，我们可以找到之前在行为分析中得出的一些元素。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t019b68763ba6d2751d.png)

如配置文件所示，jar包安装在Windows文件夹中，名为Windows.Windows，文件夹PuXpErTFKpK用于存放最终插件。配置文件中还包括释放到%TEMP%文件夹中的reg文件内容，一些杀软/安全产品的黑名单页被包含在内。

<br>

**五、功能分析**

在对大多数字符串进行去混淆之后，我们可以更好理解这款RAT的功能。通过使用JSON配置文件，该RAT可以实现功能的高度模块化，此外，程序还可以通过专用插件进行功能的扩展。

主jar包中还包含其他一些有趣的功能，比如：

1、下载其他JAR文件，以png文件保存并运行。

[![](https://p3.ssl.qhimg.com/t01ac44072dbe73aaf9.png)](https://p3.ssl.qhimg.com/t01ac44072dbe73aaf9.png)

2、捕获麦克风和摄像头数据，窥探用户隐私。

[![](https://p1.ssl.qhimg.com/t016604d2b470333387.png)](https://p1.ssl.qhimg.com/t016604d2b470333387.png)

捕获的内容被传到C&amp;C服务器上。

[![](https://p2.ssl.qhimg.com/t014ca6fa5dde1ae3c2.png)](https://p2.ssl.qhimg.com/t014ca6fa5dde1ae3c2.png)

3、在浏览器中打开指定URL。

[![](https://p4.ssl.qhimg.com/t01918bbfc02451e3d5.png)](https://p4.ssl.qhimg.com/t01918bbfc02451e3d5.png)

4、跟踪活动窗口。

[![](https://p2.ssl.qhimg.com/t01be6d324b528648f0.png)](https://p2.ssl.qhimg.com/t01be6d324b528648f0.png)

5、以报表形式将系统基本信息发送至C&amp;C服务器。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t013a8bfd63023e564d.png)

<br>

**六、总结**

恶意软件中的字符串指向jrat.io网站，并且恶意软件的功能与该网站提供的软件描述的功能十分类似。一开始我们认为它俩是同一个产品，直到在另一个研究员Matthew Mesa的提醒下，我们才发现两者的不同。细致分析jrat.io网站提供的RAT工具，我们可以看到它采用了完全不一样的类架构，jrat.io提供的RAT名为Jackbot，而本文分析的这款RAT名为Adwind（通常也称之为JRAT）。

Adwind是最受欢迎的Java RAT之一，作者在保护它的核心功能上做了许多工作以误导安全分析师。幸运的是目前为止Adwind并没有衍生出太多变种，本文分析的恶意软件与2016年7月发布的[恶意软件](https://virustotal.com/en/file/7aa15bd505a240a8bf62735a5389a530322945eec6ce9d7b6ad299ca33b2b1b0/analysis/1467618342/)十分相似。

<br>

**七、附录**

[JBifrost: Yet Another Incarnation of the Adwind RAT](https://blog.fortinet.com/2016/08/16/jbifrost-yet-another-incarnation-of-the-adwind-rat)

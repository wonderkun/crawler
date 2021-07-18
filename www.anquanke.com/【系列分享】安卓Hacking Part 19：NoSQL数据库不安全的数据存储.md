
# 【系列分享】安卓Hacking Part 19：NoSQL数据库不安全的数据存储


                                阅读量   
                                **86748**
                            
                        |
                        
                                                                                                                                    ![](./img/85780/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：infosecinstitute.com
                                <br>原文地址：[http://resources.infosecinstitute.com/android-hacking-and-security-part-19-insecure-data-storage-with-nosql-databases/](http://resources.infosecinstitute.com/android-hacking-and-security-part-19-insecure-data-storage-with-nosql-databases/)

译文仅供参考，具体内容表达以及含义原文为准

****

[![](./img/85780/t01d2a0541813adbb2d.jpg)](./img/85780/t01d2a0541813adbb2d.jpg)

翻译：[shan66](http://bobao.360.cn/member/contribute?uid=2522399780)

稿费：100RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**前言**

在上一篇文章中，我们讨论了不安全的数据存储是如何影响Android应用程序的安全性的。在本文中，我们将继续讨论不安全的数据存储问题，不过这里与数据库密切相关。

当前，NoSQL已经被各个大型公司广泛采用。像谷歌和Facebook这样的巨人也在使用NoSQL来管理他们的“大数据”。当然，NoSQL仍然在肆意蔓延—— NoSQL数据库还可用于移动应用程序。虽然针对Android系统的NoSQL解决方案有多种，但是我们这里仅介绍Couchbase Lite，在Android和iOS平台本地数据存储方面，这是一个非常不错的解决方案。

与前面讨论过的不安全数据存储概念相仿，即使以明文格式保存的NoSQL数据也可以通过各种技术（如“获取root权限的设备”、“备份技术”等）进行访问。本文将通过具体的示例应用程序为大家详细加以演示。

<br>

**NoSQL演示应用程序的功能**

让我们先看看这个应用程序的各种功能。

首先，请启动应用程序，这时将会显示如下所示的屏幕。

[![](./img/85780/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01b3961c2f8c5467b5.png)

用户可以在应用中输入卡号，然后点击提交按钮。

[![](./img/85780/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t010147060a067c93c0.png)

如果一切顺利，用户将看到一个成功消息，如下所示。

[![](./img/85780/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t014008d305eef57feb.png)

查看源代码

在这个示例中，用户输入的数据将存储在表单文档中。

下面的示例代码来自于演示应用程序的代码。



```
String dbname = "carddetails";
// create a new database
                Database database;
                try {
      database = manager.getDatabase(dbname); //manager is an object of Manager class.
} catch (CouchbaseLiteException e) {
                    return;
                }
                String cardnumber = editText.getText().toString().trim();
                Map&lt;String, Object&gt; data = new HashMap&lt;String, Object&gt;();
                data.put("cardnumber",cardnumber);
                Document document = database.createDocument();
                try {
                    document.putProperties(data);
                } catch (CouchbaseLiteException e) {
}
```

上面的代码创建了一个HashMap的对象来保存名称-值对。然后，我们创建一个文档，并将数据插入这个文档中。

测试NoSQL数据：

让我们在模拟器中安装目标应用程序，并在其中插入一些样本数据。然后，我们将考察应用程序在哪里以及如何存储我们输入的数据。

就像我们之前所做的那样，先在模拟器上获取一个shell。

键入以下命令，切换至/data/data目录。

```
cd data/data/
```

现在，让我们导航到目标包所在的目录。为此，我们可以从AndroidManifest.xml文件中通过APKTOOL找到它。

就本例来说，具体可以运行以下命令。

```
cd com.androidpentesting.couchdatastorage
```

下面，我们运行“ls”命令来查看子目录。



```
root@generic:/data/data/com.androidpentesting.couchdatastorage # ls
cache
files
lib
root@generic:/data/data/com.androidpentesting.couchdatastorage #
```

虽然这里有许多目录，却没发现名为“databases”的目录。实际上，Couchbase Lite通常会将其数据存储在“files”目录中。

所以，让我们切换到files目录，并检查其中的文件。



```
root@generic:/data/data/com.androidpentesting.couchdatastorage/files # ls
carddetails
carddetails.cblite
carddetails.cblite-journal
root@generic:/data/data/com.androidpentesting.couchdatastorage/files #
```

我们可以看到扩展名为“.cblite”的文件，这正是我们的目标应用程序所生成的数据库文件。

让我们将这个文件复制到工作站上，以便于进一步深入研究。



```
root@generic:/data/data/com.androidpentesting.couchdatastorage/files # pwd
/data/data/com.androidpentesting.couchdatastorage/files
root@generic:/data/data/com.androidpentesting.couchdatastorage/files #
```

我们可以使用“adb pull”命令将这个文件“推送”到工作站，具体如下所示。



```
srini's MacBook:Desktop srini0x00$ adb pull /data/data/com.androidpentesting.couchdatastorage/files/carddetails.cblite
1027 KB/s (114688 bytes in 0.108s)
srini's MacBook:Desktop srini0x00$
```

好了，现在我们感兴趣的东西已经到手了。

我们需要一个客户端来查看提取的数据库的内容。

Couchbase Lite Viewer是一个可用于在Mac OSX平台上面查看Couchbase Lite内容的应用程序，其下载链接如下所示：

下载链接（[http://resources.infosecinstitute.com/android-hacking-and-security-part-19-insecure-data-storage-with-nosql-databases/#download](http://resources.infosecinstitute.com/android-hacking-and-security-part-19-insecure-data-storage-with-nosql-databases/#download)  ）

下载完成后，启动程序，打开Couchbase Lite数据库。

这时，Couchbase Lite Viewer就会显示文件的内容，如上图所示。

[![](./img/85780/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01025b8b8509bf2caf.png)

如果你的系统不是Mac的话，可以使用strings命令，具体如下所示。



```
srini's MacBook:Desktop srini0x00$ strings carddetails.cblite | grep '12345'
1-2aa97aff5f838c5af074e497e8a3bd8f{"cardnumber":"12345"}
srini's MacBook:Desktop srini0x00$
```

如果您在Windows机器上无法使用字符串命令的话，可以使用Hex-Editor软件。



**<br>**

**传送门**

[**安卓 Hacking Part 1：应用组件攻防（连载）**](http://bobao.360.cn/learning/detail/122.html)

[**安卓 Hacking Part 2：Content Provider攻防（连载）**](http://bobao.360.cn/learning/detail/127.html)

[**安卓 Hacking Part 3：Broadcast Receivers攻防（连载）**](http://bobao.360.cn/learning/detail/126.html)

[**安卓 Hacking Part 4：非预期的信息泄露（边信道信息泄露）**](http://bobao.360.cn/learning/detail/133.html)

[**安卓 Hacking Part 5：使用JDB调试Java应用**](http://bobao.360.cn/learning/detail/138.html)

[**安卓 Hacking Part 6：调试Android应用**](http://bobao.360.cn/learning/detail/140.html)

[**安卓 Hacking Part 7：攻击WebView**](http://bobao.360.cn/learning/detail/142.html)

[**安卓 Hacking Part 8：Root的检测和绕过**](http://bobao.360.cn/learning/detail/144.html)

[**安卓 Hacking Part 9：不安全的本地存储：Shared Preferences**](http://bobao.360.cn/learning/detail/150.html)

[**安卓 Hacking Part 10：不安全的本地存储**](http://bobao.360.cn/learning/detail/152.html)

[**安卓 Hacking Part 11：使用Introspy进行黑盒测试**](http://bobao.360.cn/learning/detail/154.html)

[**安卓 Hacking Part 12：使用第三方库加固Shared Preferences**](http://bobao.360.cn/learning/detail/156.html)

[**安卓 Hacking Part 13：使用Drozer进行安全测试**](http://bobao.360.cn/learning/detail/158.html)

[**安卓 Hacking Part 14：在没有root的设备上检测并导出app特定的数据**](http://bobao.360.cn/learning/detail/161.html)

[**安卓 Hacking Part 15：使用备份技术黑掉安卓应用**](http://bobao.360.cn/learning/detail/169.html)

[**安卓 Hacking Part 16：脆弱的加密**](http://bobao.360.cn/learning/detail/174.html)

**[安卓 Hacking Part 17：破解Android应用](http://bobao.360.cn/learning/detail/179.html)**

[**安卓 Hacking Part 18：逆向工程入门篇******](http://bobao.360.cn/learning/detail/3648.html)

<br>

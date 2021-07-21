> 原文链接: https://www.anquanke.com//post/id/157513 


# ghostscript命令执行漏洞预警


                                阅读量   
                                **205109**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                    



[![](https://p0.ssl.qhimg.com/t012c3dcf6c3f18f24a.jpg)](https://p0.ssl.qhimg.com/t012c3dcf6c3f18f24a.jpg)

## 0x00 漏洞背景

8 月 21 号，Tavis Ormandy 通过公开邮件列表（hxxps://bugs.chromium[.]org/p/project-zero/issues/detail?id=1640），再次指出 ghostscript 的安全沙箱可以被绕过，通过构造恶意的图片内容，可造成命令执行。

ghostscript应用广泛，ImageMagick、python-matplotlib、libmagick 等图像处理应用均有引用。

在ghostscript中由于以往的安全事件，针对安全问题gs官方采用增加参数-dSAFER来开启安全沙箱，但该沙箱在程序执行过程中由LockSafetyParams这个值进行控制，此次Taviso发现通过restore操作会将该值成功覆盖，导致安全沙箱被绕过，引发命令执行漏洞。



## 0x01 漏洞影响

version &lt;= 9.23（全版本、全平台）

官方未出缓解措施，最新版本受到影响。

漏洞导致所有引用ghostscript的上游应用收到影响。 常见应用如下：
- imagemagick
- libmagick
- graphicsmagick
- gimp
- python-matplotlib
- texlive-core
- texmacs
- latex2html
- latex2rtf
等



## 0x02 详细分析

对ghostscript进行调试。

[![](https://p403.ssl.qhimgs4.com/t01319f299b61876421.jpeg)](https://p403.ssl.qhimgs4.com/t01319f299b61876421.jpeg)

可以看到在此处因为-dSAFER 被置为1

[![](https://p403.ssl.qhimgs4.com/t01b76196f070755bf7.png)](https://p403.ssl.qhimgs4.com/t01b76196f070755bf7.png)

可以看到这里因为restore操作成功绕过了限制将LockSafetyParams成功置为0

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p403.ssl.qhimgs4.com/t01b730e2c22c6217be.jpeg)

[![](https://p403.ssl.qhimgs4.com/t011fcc2c3f628725e6.jpeg)](https://p403.ssl.qhimgs4.com/t011fcc2c3f628725e6.jpeg)

在最后调用pope执行%pipe%命令之前的函数中依旧为0并且没有任何操作将LockSafetyParams的值修复。成功造成命令执行。

[![](https://p403.ssl.qhimgs4.com/t0112ec5889882d55fd.jpeg)](https://p403.ssl.qhimgs4.com/t0112ec5889882d55fd.jpeg)

可见命令直接被带入popen函数。



## 0x03 利用效果

漏洞利用效果如下： [![](https://p403.ssl.qhimgs4.com/t013f1ac13b0f39b593.png)](https://p403.ssl.qhimgs4.com/t013f1ac13b0f39b593.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p403.ssl.qhimgs4.com/t0133b430877895ddf4.png)



## 0x04 缓解措施

目前官方未给出缓解措施，建议卸载ghostscript。

使用ImageMagick，建议修改policy文件（默认位置：/etc/ImageMagick/policy.xml），在 &lt;policymap&gt; 中加入以下 &lt;policy&gt;（即禁用 PS、EPS、PDF、XPS coders）：

```
&lt;policymap&gt;
&lt;policy domain="coder" rights="none" pattern="PS" /&gt;
&lt;policy domain="coder" rights="none" pattern="EPS" /&gt;
&lt;policy domain="coder" rights="none" pattern="PDF" /&gt;
&lt;policy domain="coder" rights="none" pattern="XPS" /&gt;
&lt;/policymap&gt;
```



## 0x05 时间线

**2018-08-18** taviso提交漏洞

**2018-08-22** 漏洞信息公开

**2018-08-22** 360CERT对漏洞分析跟进，发布预警分析



## 0x06 参考链接
1. [邮件列表](https://bugs.chromium.org/p/project-zero/issues/detail?id=1640)
1. [Ghostscript sandbox bypass lead ImageMagick to remote code execution](http://seclists.org/fulldisclosure/2016/Oct/77)
1. [multiple ghostscript -dSAFER sandbox problems](http://seclists.org/oss-sec/2016/q4/29)
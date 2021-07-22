> 原文链接: https://www.anquanke.com//post/id/86153 


# 【Pwn2own漏洞分享系列】利用macOS内核漏洞逃逸Safari沙盒


                                阅读量   
                                **74098**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t0188630f884d61fd53.png)](https://p0.ssl.qhimg.com/t0188630f884d61fd53.png)

**作者：360vulcan团队**

**<br>**

**背景**<br>



在Pwn2own 2017 比赛中，苹果的macOS Sierra 和 Safari 10 成为被攻击最多的目标之一。在此次比赛过程中，尽管有多支战队成功/半成功地完成了对macOS + Safari目标的攻破，然而360安全战队使用的漏洞数量最少，而且也是唯一一个通过内核漏洞实现沙盒逃逸和提权，并完全控制macOS操作系统内核的战队。在这篇技术分享中，我们将介绍我们所利用的macOS内核漏洞的原理和发现细节。

在Pwn2own 2017中，为了完全攻破macOS Sierra + Safari目标，彻底控制操作系统内核，360安全战队使用了两个安全漏洞： 一个Safari远程代码执行漏洞（CVE-2017-2544）和一个macOS内核权限提升漏洞（CVE-2017-2545)。CVE-2017-2545是存在于macOS IOGraphics组件中的安全漏洞。

从互联网上可循的源码历史来看，该漏洞最早在1992年移植自Joe Pasqua的代码，因此这个漏洞已经在苹果操作系统中存在了超过25年，几乎影响苹果电脑的所有历史版本，同时这又是可以无视沙盒的限制，直接从沙盒中攻入内核的漏洞。

在我们3月比赛中奖漏洞负责任报告给苹果公司后，苹果已经在5月15日发布的macOS Sierra 10.12.5中修复了该漏洞。



**寻找浏览器可访问的内核驱动**



和Windows系统一样，Safari的浏览器沙盒限制了沙盒内进程可访问的内核驱动，以减小内核攻击面对沙盒逃逸攻击的影响，因此我们进行的第一步研究就是寻找在浏览器沙盒内可访问的内核驱动接口。

在macOS 上，系统根据下面两个沙盒规则文件定义了Safari浏览器的权限范围。

/System/ Library/Sandbox/Profiles/system.sb

/System/Library/Frameworks/WebKit.framework/Versions/A/Resources/com.apple.WebProcess.sb

我们进一步关注Safari浏览器能够访问的内核驱动种类。在system.sb文件中，我们发现这样一个规则：

(allow iokit-open (iokit-registry-entry-class “IOFramebufferSharedUserClient”))

这个规则说明Safari浏览器可以打开IOFramebufferSharedUserClient这个驱动接口。IOFramebufferSharedUserClient是IOGraphic内核组件向用户态提供的接口。IOGraphic是macOS上的核心基础驱动，负责图形图像处理任务，10.12.4版本上对应的IOGraphic源码包在：https://opensource.apple.com/source/IOGraphics/IOGraphics-514.10/ 。既然IOGraphic相关代码是开源的，那么在下一步，我们就对IOGraphic进行了代码审计。

<br>

**攻击面**



IOFramebufferSharedUserClient 继承于IOUserClient。用户态可以通过匹配名“IOFramebuff”的IOService, 然后调用IOServiceOpen函数获IOFramebufferSharedUserClient对象的端口。

在获取一个IOUserClient对象port后，我们通过用户态API IOConnectCallMethod可以触发内核执行这个对象的 ::externalMethod接口； 通过用户态API IOConnectMapMemory可以触发内核执行这个对象的 ::clientMemoryForType接口; 通过用户态API  IOConnectSetNotificationPort可以触发内核执行这个对象的 ::registerNotificationPort接口。

实际上IOFramebufferSharedUserClient提供的用户态接口很少，其中函数IOFramebufferSharedUserClient::getNotificationSemaphore 引起了我们关注。在IOKit.framework中，实际上有个未导出的函数io_connect_get_notification_semaphore， 通过这个API，我们可以触发内核执行相应IOUserClient对象的 ::getNotificationSemaphore接口。

漏洞：getNotificationSemaphore UAF

我们参考IOFramebufferSharedUserClient::getNotificationSemaphore的接口代码



```
接口也很简单，代码如下：
IOReturn IOFramebufferSharedUserClient::getNotificationSemaphore(
   UInt32 interruptType, semaphore_t * semaphore )
`{`
   return (owner-&gt;getNotificationSemaphore(interruptType, semaphore));
`}`
```

由此可见， IOFramebufferSharedUserClient::getNotificationSemaphore直接调用的是它的所有者 （也就是IOFramebuffer实例）的getNotificationSemaphore接口。



```
OFramebuffer::getNotificationSemaphore代码如下：

IOReturn IOFramebuffer::getNotificationSemaphore(
   IOSelect interruptType, semaphore_t * semaphore )
`{`
   kern_return_t       kr;
   semaphore_t         sema;

   if (interruptType != kIOFBVBLInterruptType)
       return (kIOReturnUnsupported);

   if (!haveVBLService)
       return (kIOReturnNoResources);

   if (MACH_PORT_NULL == vblSemaphore)
   `{`
       kr = semaphore_create(kernel_task, &amp;sema, SYNC_POLICY_FIFO, 0);
       if (kr == KERN_SUCCESS)
           vblSemaphore = sema;
   `}`
   else
       kr = KERN_SUCCESS;

   if (kr == KERN_SUCCESS)
       *semaphore = vblSemaphore;

   return (kr);
`}`
```

通过上面的代码大家可以看出来，vblSemaphore是一个全局对象成员。vblSemaphore初始值为0。这个函数第一次执行后，内核调用semaphore_create，创建一个信号量，将其赋予vblSemaphore。后面这个函数再次执行时就会直接返回vblSemaphore。

问题在于，用户态调用io_connect_get_notification_semaphore获取信号量后，可以销毁该信号量。此时，内核中vblSemaphore仍指向一个已经销毁释放的信号量对象。

当用户态继续调用io_connect_get_notification_semaphore获取vblSemaphore并使用该信号量时，就会触发UAF（释放后使用）的情况。



**总结**



IOUserClient框架提供了大量接口给用户态程序。由于历史原因，IOFramebufferSharedUserClient仍然保留一个罕见的接口。尽管用户态的IOKit.framework中没有导出相应的API，这个接口仍然可以调用，我们可以把内核中 IOFramebuffer::getNotificationSemaphore的UAF问题，转化为内核地址信息泄漏和任意代码执行，实现浏览器的沙盒逃逸和权限提升。



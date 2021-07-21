> 原文链接: https://www.anquanke.com//post/id/87115 


# 【技术分享】Form-Grabber恶意软件的详细分析


                                阅读量   
                                **81504**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：stormshield.com
                                <br>原文地址：[https://thisissecurity.stormshield.com/2017/09/28/analyzing-form-grabber-malware-targeting-browsers/](https://thisissecurity.stormshield.com/2017/09/28/analyzing-form-grabber-malware-targeting-browsers/)

译文仅供参考，具体内容表达以及含义原文为准

![](https://p4.ssl.qhimg.com/t0185e66e5f7550a9fb.jpg)



译者：[WisFree](http://bobao.360.cn/member/contribute?uid=2606963099)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

**介绍**

****

作为Stormshield安全情报团队的一名新成员，我的第一个任务就是分析这款form-grabber恶意软件，在这种恶意软件的帮助下，攻击者可以利用基于Web浏览器的注入方法来窃取目标用户的密码。在这篇文章中，我将跟大家详细介绍这款恶意软件的技术细节，其中的重点是Web浏览器的注入技术。

这款恶意软件已经有一定“年纪”了，因为从编译后代码的时间戳来看，这款恶意软件早在2012年就已经存在了。但是待会儿等我介绍完之后你就会发现，虽然这款恶意软件已经“上年纪”了，但它仍然能够高效地攻击很多最新版本的浏览器（32位模式）。安全研究专家[Xylitol](https://twitter.com/Xylit0l)已经在[VirusTotal](https://www.virustotal.com/en/file/9cdb1a336d111fd9fc2451f0bdd883f99756da12156f7e59cca9d63c1c1742ce/analysis/1355250283/)平台上传了一份这款恶意软件的样本，但是目前互联网上还没有针对这款恶意软件的详细分析报告。由于这部分内容的缺失，这种威胁的传播方法很可能不为人所知，这也是我写这篇文章的原因。

<br>

**脱壳**

****

我们所分析的样本加了两层壳，第一层是UPX的壳，这个可以轻松脱壳。第二层同样非常简单，它利用了一种反调试技巧读取PEB中的‘**BeingDebugged**’标记。除此之外，这里还实现了一种反混淆技术，即样本使用了一个1字节密钥（0x0F）来进行XOR运算并输出解密后的PE域（缓冲区使用**VirtualAlloc()**分配）。在调用了**VirtualAlloc**()之后，我们可以使用下列指令来识别第二阶段的壳是否结束：



```
push 0x666 ; magic value checked after unpacking
push ebx   ; base address of the unpacked PE
call eax   ; leads to the unpacked PE original entry point
```

因此我们可以得知，这款恶意软件在执行第一个功能时需要接收两个输入参数：

**脱壳后的PE基地址；**

**一个可当作密钥使用的值；**

如果这个值不是恶意软件所定义的（0x666），那么它就会停止运行。

<br>

**RC4加密**

****

为了防止逆向分析或其他基于检测的静态分析方法，这款恶意软件使用了RC4算法来加密字符串。其中被加密的绝大多数都是与Web浏览器注入相关的DLL、函数名称或参数，它们可以使用**LoadLibraryA()**和**GetProcAddress()**来动态解析导入的代码库。在地址data+0x30中有一个结构体数组，其中包含有每一个加密字符串的地址。这个结构体如下代码所示：



```
struct rc4_encrypted_string `{`
    const char *string;  // pointer to the encrypted string stored in .rdata
    unsigned int length; // length of the string
`}`
```

因此，为了解密字符串，恶意软件使用了一个函数来发送结构体数组中加密字符串的个数，并以此来推算其所在地址和长度。在一个IDA Python脚本的帮助下，我们可以轻松找到这个函数的交叉引用，并了解到字符串的个数，并执行解密。

运行脚本之后，我们可以发现很多有意思的字符串，例如DLL或函数名等等：

![](https://p5.ssl.qhimg.com/t01858daac62cf3f2da.png)

用于解密的RC4密钥长度为128位，其地址存放于data+0x14。在这个样本中，其密钥为：27F56A32B728364FBA109F983D148023。

<br>

**主要的执行流程**

****

这款恶意软件的主线程用来执行一个无限循环，然后在循环中枚举出目标操作系统中正在运行的所有进程，最终找出一个浏览器程序并实现线程注入。枚举过程主要使用了以下几个Windows API函数：

**CreateToolhelp32Snapshot()**

**Process32FirstW()**

**Process32NextW()**

这款恶意软件还会寻找任何名字符合以下字符串的进程，并尝试向其中注入一个线程：

**chrome.exe**

**firefox.exe**

**opera.exe**

**iexplorer.exe**

**WebKit2WebProcess.exe (Safari)**

<br>

**Form-grabber线程注入**

****

一旦其找到了匹配的进程名称，它便会调用**OpenProcess()**来获取目标进程的控制权。接下来，恶意软件将调用**VirtualAlloc()**在目标进程的地址空间中分配一个执行的内存区域。这一块内存区域可以用来存储当前运行的PE文件副本（使用**WriteProcessMemory()**实现）。现在，整个PE文件都会被映射到目标进程的地址空间中，最后再调用**CreateRemoteThread()**来运行注入的线程。

由于这款恶意软件不会向线程函数传递任何的变量，因此远程线程不需要知道它到底是在哪个进程中运行的。

<br>

**内联钩子**

****

内联钩子（Inline Hooking）是一种专门用来拦截函数调用的方法，这种方法可以执行一种旁路函数来访问原始函数的参数信息。在我们的分析样本中，它使用了这种内联钩子来拦截浏览器在发送HTTP请求时所调用的函数，并访问其中包含的敏感数据，例如用户名、密码或信用卡号等等。

为了设置内联钩子，这款恶意软件使用了一个全局结构体来存储挂钩函数的信息（存储在.data域）。这种结构体如下代码所示：



```
// Function pointer definition for calling HTTPSendRequestA()
typedef BOOL (*http_send_request_prototype_t)(
  _In_ HINTERNET hRequest,
  _In_ LPCTSTR   lpszHeaders,
  _In_ DWORD     dwHeadersLength,
  _In_ LPVOID    lpOptional,
  _In_ DWORD     dwOptionalLength
);
 
struct direct_injection_hook `{`
   http_send_request_prototype_t hooked_function; // address of Wininet.dll!HttpSendRequestA
   http_send_request_prototype_t detour_function; // address of the function written by the author
   unsigned int count_saved_bytes;                // number of bytes overriden at Wininet.dll!HttpSendRequestA
   void (*return_to_dll)(void);                   // address of user-allocated page (RWX) used to execute the original
                                                  // hooked function after execution of the detour function
`}`
```

下面是用于设置内联钩子的函数反编译版本，代码位于地址.text+0x40：

![](https://p2.ssl.qhimg.com/t011e3c101cf0894035.png)

<br>

**挂钩后的执行流程**

****

当设置好了钩子之后，如果iexplorer.exe调用了**Wininet.dll!HttpSendRequestA**，则执行流程如下：

1.       执行**Wininet.dll!HttpSendRequestA**的第一条指令，并跳转到旁路函数。

2.       旁路函数访问已挂钩函数的参数信息，例如HTTP Payload，并从中提取出敏感数据。

3.       旁路函数调用跳转函数（return_to_dll），并存储**Wininet.dll!HttpSendRequestA**执行过的所有指令，最终跳转到**Wininet.dll!HttpSendRequestA**+5然后执行。

4.       **Wininet.dll!HttpSendRequestA**剩下的指令会继续执行，直到函数返回并执行HTTP请求。

5.       旁路函数运行完之后会返回到原函数，然后调用**Wininet.dll!HttpSendRequestA**。

完整的执行流程请大家参考下面这张图片：

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

<br>

**浏览器与挂钩函数信息**

****

下面这个表格显示的是浏览器可注入的DLL和函数名等信息：

![](https://p4.ssl.qhimg.com/t012168f3c815087d3e.png)

某些函数是在HTTP层运行的，这也就意味着当用户浏览一个HTTPS网站时，函数钩子在将信息传递给TLS层并进行加密之前，它首先拼接出的会是HTTP请求。剩下的操作全部都会在TCP层执行，这也就意味着浏览一个HTTPS网站将会导致恶意软件挂钩TLS记录Payload并通过套接字进行发送，而这对于这款恶意软件来说没有任何的实际意义。

该恶意软件基于**BaseHTTPServer**所创建出的类代码如下，其主要功能就是捕获POST方法：



```
import BaseHTTPServer
import urlparse
 
browser_mapping = `{`
    0 : 'chrome.exe',
    1 : 'chrome.exe',
    2 : 'firefox.exe',
    3 : 'opera.exe',
    4 : 'WebKit2WebProcess.exe', # Safari
    5 : 'iexplorer.exe'
`}`
 
HOST='localhost'
PORT=80
XOR_KEY=0x07
 
class FormGrabberHTTPDecoder(BaseHTTPServer.BaseHTTPRequestHandler):
 
    def do_POST(self):
        request_line = self.requestline
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        decoded_data = urlparse.parse_qs(post_data)
        malware_version = decoded_data['v'][0]
        injected_browser =  browser_mapping[int(decoded_data['t'][0])]
        username_hostname = decoded_data['h'][0]
        hexdumped_post_data = decoded_data['c'][0]
        xored_post_data = hexdumped_post_data.decode('hex')
        unxored_post_data = [chr(ord(c) ^ XOR_KEY) for c in xored_post_data]
        unxored_post_data = ''.join(unxored_post_data)
        d1 = ('-' * 79)
        d2 = ('*' * 79)
        print('Received HTTP request line: `{``}`'.format(request_line))
        print('Received HTTP body:n`{``}`n`{``}`n`{``}`'.format(d1, post_data, d1))
        print('Malware version: `{``}`'.format(malware_version))
        print('Injected browser: `{``}`'.format(injected_browser))
        print('Username and Hostname: `{``}`'.format(username_hostname))
        print('Intercepted HTTP request:n`{``}`n`{``}`n`{``}`'.format(
            d1, unxored_post_data, d1))
        print(d2)
 
if __name__ == '__main__':
    s = BaseHTTPServer.HTTPServer((HOST, PORT), FormGrabberHTTPDecoder)
s.serve_forever()
```

下面是脚本的输出样本，我们尝试通过facebook.com的身份验证，测试环境为IE浏览器+HTTPS：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](http://p0.qhimg.com/t01dbc44cb7b30411a8.png) 



**浏览器测试**

****

因为这款form-grabber恶意软件在我分析的时候已经存在了五年之久了，所以我们也很想知道为什么它至今仍然可以攻击很多最新版本的浏览器。实际上在这些年里，浏览器的架构一直都在不断地升级和改进，而这款恶意软件所挂钩的部分函数现在已经不再使用了。下面这个表格所显示的内容是这款恶意软件在Windows 7操作系统（SP1，64位）中可以成功攻击的浏览器版本信息：

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

有意思的是，除了Firefox之外，该恶意软件所有的函数钩子都可以有效地对所有最新版本的32位浏览器实施攻击。

<br>

**总结**

****

这是一款十分精巧的form-grabber型恶意软件，它使用了一些反调试技术，并对函数调用进行了混淆处理。除此之外，它还使用了RC4算法来加密函数以及DLL名称来执行代码库的动态导入。众所周知，内联钩子是一种用于拦截函数调用的著名技术，而且对于目前最新版本的浏览器来说这种技术仍然是非常有效的。但是，这款恶意软件的开发者并没有花时间去优化所有浏览器HTTP层的钩子函数，因此它很有可能无法针对那些通过https来发送的请求进行拦截和攻击。

<br>

**额外信息**

****

MD5: cb066c5625aa85957d6b8d4caef4e497

SHA1: bd183265938f81990260d88d3bb6652f5b435be7

SHA256: 9cdb1a336d111fd9fc2451f0bdd883f99756da12156f7e59cca9d63c1c1742ce

VirusTotal的分析报告：【[传送门](https://www.virustotal.com/en/file/9cdb1a336d111fd9fc2451f0bdd883f99756da12156f7e59cca9d63c1c1742ce/analysis/1355250283/)】

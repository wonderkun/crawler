> 原文链接: https://www.anquanke.com//post/id/225028 


# 病毒作者利用破解去广告腾讯视频噱头投递CS后门


                                阅读量   
                                **299870**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">5</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



## 背景

近日接到用户反馈，发现一起通过腾讯视频精简包投毒事件。经过分析，发现该安装包携带Cobalt Strike后门病毒。用户安装腾讯视频精简包并运行腾讯视频主程序后，就会激活后门病毒。病毒可以接收C&amp;C服务器指令，具备服务创建，进程注入，远程shell等功能。



## 详情

攻击诱饵使用了白加黑利用进行Dll劫持，利用腾讯视频主程序加载伪造的HttpModule.dll内存执行key.bin中的shellcode，shellcode执行下载的ByPQ经过解密，最终投递出Cobalt Strike Beacon后门

整体攻击流程如下：

[![](https://p3.ssl.qhimg.com/t011922da8340f5067a.png)](https://p3.ssl.qhimg.com/t011922da8340f5067a.png)



## 样本分析

腾讯视频 11.9.3255 去广告精简版.exe为一安装包，安装后的目录结构

[![](https://p2.ssl.qhimg.com/t01085e416373d311c5.png)](https://p2.ssl.qhimg.com/t01085e416373d311c5.png)

运行腾讯主程序后得到如下进程树

[![](https://p4.ssl.qhimg.com/t012e7bd0337431d6fa.png)](https://p4.ssl.qhimg.com/t012e7bd0337431d6fa.png)

分析后发现伪造的HttpModule.dll通过QQLive.exe加载执行cmd.exe /c Crack.exe key.bin

### <a class="reference-link" name="HttpModule.dll%E5%88%86%E6%9E%90"></a>HttpModule.dll分析

HttpModule.dll的基本信息如下

|文件名|HttpModule.dll
|------
|SHA1|2fcd53bc8a641f2dad7dc22fb3650e4f4a8c94b7
|文件格式|PE文件（Dll）
|时间戳|2020.11.21 03:07:39

携带伪造的数字签名

[![](https://p5.ssl.qhimg.com/t01658b61b9d69c8222.png)](https://p5.ssl.qhimg.com/t01658b61b9d69c8222.png)

HttpModule.dll被加载后，创建cmd进程执行命令

[![](https://p3.ssl.qhimg.com/t0109abcf56f4079d4b.png)](https://p3.ssl.qhimg.com/t0109abcf56f4079d4b.png)

### <a class="reference-link" name="Crack.exe%E5%88%86%E6%9E%90"></a>Crack.exe分析

Crack.exe的基本信息如下

|文件名|Crack.exe
|------
|SHA1|1a54517f881807962d9f0070a83ce9b77552f7bc
|文件格式|PE文件（exe）
|时间戳|2020.11.21 02:31:31

Crack.exe的功能很单一，是一个shellcode加载器，用于读取key.bin并加载执行

[![](https://p1.ssl.qhimg.com/t01a746792064b8741d.png)](https://p1.ssl.qhimg.com/t01a746792064b8741d.png)

### <a class="reference-link" name="Key.bin%E5%88%86%E6%9E%90"></a>Key.bin分析

这段shellcode代码利用PEB以及PE结构查找函数

[![](https://p1.ssl.qhimg.com/t010b6849934f6798f5.png)](https://p1.ssl.qhimg.com/t010b6849934f6798f5.png)

看上述代码有些熟悉，便使用cs生成一段payload

[![](https://p2.ssl.qhimg.com/t012febc9952aec9ddb.png)](https://p2.ssl.qhimg.com/t012febc9952aec9ddb.png)

对比代码，判断该代码是属于cs生成的

[![](https://p1.ssl.qhimg.com/t014e192b170feeb89e.png)](https://p1.ssl.qhimg.com/t014e192b170feeb89e.png)

获取函数后执行请求svchosts.ddns.net:4447/ByPQ，在内存中加载

[![](https://p4.ssl.qhimg.com/t01143625a10e39ae70.png)](https://p4.ssl.qhimg.com/t01143625a10e39ae70.png)

[![](https://p0.ssl.qhimg.com/t01ca19aceabfa62803.png)](https://p0.ssl.qhimg.com/t01ca19aceabfa62803.png)

### <a class="reference-link" name="ByPQ%E5%88%86%E6%9E%90"></a>ByPQ分析

ByPQ同样是一段shellcode，最前面0x44字节的代码负责解密0x44偏移后的数据，解密出的是个pe文件

[![](https://p4.ssl.qhimg.com/t011ba781cc839576f7.png)](https://p4.ssl.qhimg.com/t011ba781cc839576f7.png)

dump解密后的pe文件

dll名为beacon.dll，导出函数为ReflectiveLoader

[![](https://p3.ssl.qhimg.com/t01e75bf5c83c704c3f.png)](https://p3.ssl.qhimg.com/t01e75bf5c83c704c3f.png)

解密出pe文件后直接通过偏移调用ReflectiveLoader将beacon.dll在内存中加载

[![](https://p3.ssl.qhimg.com/t01af6d9ff6315e8573.png)](https://p3.ssl.qhimg.com/t01af6d9ff6315e8573.png)

该后门文件存在近100个C2命令，包含服务创建，进程注入，远程shell等功能

[![](https://p3.ssl.qhimg.com/t01a41d613105cb93d6.png)](https://p3.ssl.qhimg.com/t01a41d613105cb93d6.png)

访问svchosts.ddns.net:4447/activity

由于C2服务器已经失效，无法获取后续更多信息

[![](https://p0.ssl.qhimg.com/t0101b5667b8e7ecb5d.png)](https://p0.ssl.qhimg.com/t0101b5667b8e7ecb5d.png)



## 其他信息

该精简包最开始出现的地方应该是吾爱破解，但是分析时原帖已经被删，在其他网站上也发现了类似的发帖，发帖时间是11月21号的9点，与恶意程序时间戳上的时间相对应，病毒作者将恶意程序与腾讯视频打包后便将后门程序进行投放

[![](https://p1.ssl.qhimg.com/t01fb8f244206a60def.png)](https://p1.ssl.qhimg.com/t01fb8f244206a60def.png)



## 总结

病毒作者利用破解去广告的噱头吸引用户去下载带毒程序，白利用与shellcode加载已经可以对绝大部分安全软件进行绕过

即使有安全软件报毒，用户也会误以为是对“灰色软件”的不信任，从而放弃查杀

由于软件对自身加载的文件缺少校验，才使得白利用的情况愈演愈烈，希望软件厂商能够加强对自身文件的校验



## 安全建议

提高安全意识，所有软件在官网下载，不下载第三方及来历不明的软件

对于安全软件报毒的程序，不轻易添加信任或者退出安全软件



## IOCs

SHA1

2f3cacd0ea26c30fa5191ae1034bb74bf2cc3208 (key.bin)

1a54517f881807962d9f0070a83ce9b77552f7bc (Crack.exe)

546f6b916f15d750006dbcc9f615a6612b6660b2 (beacon.dll)

5ac72ba3cc39d30dfb5605a1bbb490cb6d32c0b9 (ByPQ)

2fcd53bc8a641f2dad7dc22fb3650e4f4a8c94b7 (HttpModule.dll)

09264a40e46dff6d644d1aa209d61da31a70bc7d (腾讯视频 11.9.3255 去广告精简版.exe)

C2

svchosts.ddns.net:4447

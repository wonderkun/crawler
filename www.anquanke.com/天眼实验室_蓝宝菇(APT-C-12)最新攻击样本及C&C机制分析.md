> 原文链接: https://www.anquanke.com//post/id/152639 


# 天眼实验室：蓝宝菇(APT-C-12)最新攻击样本及C&amp;C机制分析


                                阅读量   
                                **162055**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t0100fe88ec7716f64f.jpg)](https://p5.ssl.qhimg.com/t0100fe88ec7716f64f.jpg)



## 背景

继360公司披露了蓝宝菇(APT-C-12)攻击组织的相关背景以及更多针对性攻击技术细节后，360威胁情报中心近期又监测到该组织实施的新的攻击活动，本文章是对其相关技术细节的详细分析。



## 样本分析

### 诱饵文件

在APT-C-12组织近期的攻击活动中，其使用了伪装成”中国轻工业联合会投资现况与合作意向简介”的诱导文件，结合该组织过去的攻击手法，该诱饵文件会随鱼叉邮件进行投递。

如下图所示该诱饵文件伪装成文件夹的图标，执行后会打开包含有诱饵文档和图片的文件夹，而此时实际的恶意载荷已经在后台执行。

[![](https://p3.ssl.qhimg.com/t01cbc54b68402dbb36.png)](https://p3.ssl.qhimg.com/t01cbc54b68402dbb36.png)

当该诱饵文件运行时，其会解密释放4个文件，其中两个为上述的诱导文档和图片，另外为两个恶意的tmp文件。

[![](https://p5.ssl.qhimg.com/t017125f8050e4e22ab.png)](https://p5.ssl.qhimg.com/t017125f8050e4e22ab.png)

释放的恶意tmp文件路径为：

```
%temp%\unicode32.tmp
%appdata%\WinRAR\update.tmp
```

最后通过LoadLibraryW加载释放的unicode32.tmp文件。

[![](https://p3.ssl.qhimg.com/t01d0aa4f288ec22dec.png)](https://p3.ssl.qhimg.com/t01d0aa4f288ec22dec.png)

### unicode32.tmp

unicode32.tmp为一个loader，其主要用于加载update.tmp，如下图所示其通过rundll32.exe加载update.tmp，并调用其导出函数jj。

[![](https://p5.ssl.qhimg.com/t013aa021c83b03cda9.png)](https://p5.ssl.qhimg.com/t013aa021c83b03cda9.png)

当加载了update.tmp后，会删除装载exe程序文件和自身。

[![](https://p4.ssl.qhimg.com/t01dddb036be7ebe275.png)](https://p4.ssl.qhimg.com/t01dddb036be7ebe275.png)

[![](https://p1.ssl.qhimg.com/t0102739e236f9201f0.png)](https://p1.ssl.qhimg.com/t0102739e236f9201f0.png)

### update.tmp

该文件为一个DLL,并有一个名为jj的导出函数。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01805716fe1939c6d1.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01cebb587b786208b4.png)

其首先会对目标主机进行信息收集。

1.获取系统版本信息[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t011dd85b75061ccda5.png)2.调用CreateToolhelp32Snapshot获取系统进程信息。[![](https://p2.ssl.qhimg.com/t01fdcb7ae4328aaa9f.png)](https://p2.ssl.qhimg.com/t01fdcb7ae4328aaa9f.png)3.调用GetAdaptersInfo获取网卡MAC地址。[![](https://p1.ssl.qhimg.com/t01fb35b49c110b3ff0.png)](https://p1.ssl.qhimg.com/t01fb35b49c110b3ff0.png)4.判断当前系统环境是32位或64位。[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t011718306b3322c469.png)5.通过注册表获取已安装的程序信息，获取的安装程序信息加上前缀”ISL”格式化。

[![](https://p0.ssl.qhimg.com/t0106e865c0397ca468.png)](https://p0.ssl.qhimg.com/t0106e865c0397ca468.png)

[![](https://p5.ssl.qhimg.com/t01d639a37ad16c2742.png)](https://p5.ssl.qhimg.com/t01d639a37ad16c2742.png)6.通过注册表获取DisplayName和DisplayVersion的信息，并将DisplayName 和DisplayVersion格式化为”%s”:`{`“ND”:”%s”,”DV”:”%s”`}`。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01fe12bc76023b7183.png)

[![](https://p2.ssl.qhimg.com/t0194b798e735de6759.png)](https://p2.ssl.qhimg.com/t0194b798e735de6759.png)

信息收集后会首先向远程控制服务器发送上线信息。[![](https://p4.ssl.qhimg.com/t01a3ebec5ce85d21e7.png)](https://p4.ssl.qhimg.com/t01a3ebec5ce85d21e7.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0180c65e27bd892fd6.png)

获取tmp目录, 创建AdobeNW目录,并从控制服务器上下载AdobeUpdate.tmp作为第二阶段的载荷，其实际为一个DLL文件。

[![](https://p0.ssl.qhimg.com/t01c00831b1ad72292a.png)](https://p0.ssl.qhimg.com/t01c00831b1ad72292a.png)

[![](https://p5.ssl.qhimg.com/t015a38c3534a684373.png)](https://p5.ssl.qhimg.com/t015a38c3534a684373.png)

[![](https://p5.ssl.qhimg.com/t018bf33a16152e289e.png)](https://p5.ssl.qhimg.com/t018bf33a16152e289e.png)

最终调用rundll32启动DLL文件的导出函数MainFun,如果进程创建成功给服务器返回信息。

[![](https://p1.ssl.qhimg.com/t016bb75eb4d24979f2.png)](https://p1.ssl.qhimg.com/t016bb75eb4d24979f2.png)

### AdobeUpdate.tmp

AdobeUpdate.tmp为DLL文件，其导出方法MainFun由第一阶段木马DLL调用执行。[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01ffea72607670c729.png)

其首先遍历%USERPROFILE%\\AppData路径下tmp后缀文件，并删除。[![](https://p2.ssl.qhimg.com/t01fdee2c22b0b53c58.png)](https://p2.ssl.qhimg.com/t01fdee2c22b0b53c58.png)

然后从文件自身尾部读取配置信息并解密，其格式如下：

加密的配置信息，包括标识ID，控制服务器地址，加密IV和KEY，以及Mutex信息；

4字节加密配置信息长度；

17字节解密密钥；[![](https://p0.ssl.qhimg.com/t01c064c5bc70201bc9.png)](https://p0.ssl.qhimg.com/t01c064c5bc70201bc9.png)

例如上图所示的解密配置文件的KEY为sobcsnkciatwiffi，其解密算法如下。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01205587f0eb34335f.png)

[![](https://p5.ssl.qhimg.com/t015c31f3ae3b1fe7a5.png)](https://p5.ssl.qhimg.com/t015c31f3ae3b1fe7a5.png)

解密之后的配置文件如下所示。[![](https://p2.ssl.qhimg.com/t01252b1b0194e56300.png)](https://p2.ssl.qhimg.com/t01252b1b0194e56300.png)

查询HKEY_CURRENT_USER下的MyApp注册表查看是否有FirstExec, 通过字符串”no”来判断该DLL是否是第一次执行。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01c6bc2b9238b956cf.png)

若DLL不为首次执行，则轮询获取控制服务器命令，否则遍历磁盘C：到F：中的文档文件信息，并保存在temp文件夹下的list_tmp.txt中。

[![](https://p4.ssl.qhimg.com/t0153f199bbd19e04a5.png)](https://p4.ssl.qhimg.com/t0153f199bbd19e04a5.png)

[![](https://p3.ssl.qhimg.com/t0189620e25f910036e.png)](https://p3.ssl.qhimg.com/t0189620e25f910036e.png)

其中查找的文档类型包括.ppt .pptx .pdf .xls .xlsx .doc .docx .txt .wps .rtf的文档，将文档文件路径、创建时间以及文件大小信息进行保存。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01d96a904834d840ef.png)

下图为示例的写入数据格式(文件路径 创建时间 文件大小):

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t014a883b6d4eb51d5f.png)

并将list_tmp.txt进行aes加密后上传到控制服务器。[![](https://p3.ssl.qhimg.com/t012fc040418edb82d8.png)](https://p3.ssl.qhimg.com/t012fc040418edb82d8.png)

接着设置注册表FirstExec标志。[![](https://p2.ssl.qhimg.com/t016d0d54f1f515ccd4.png)](https://p2.ssl.qhimg.com/t016d0d54f1f515ccd4.png)

AdobeUpdate.dll木马实现了丰富的命令控制指令，其通过访问控制域名获取包含有控制命令的文件，并在本地解密解析后执行。

[![](https://p0.ssl.qhimg.com/t01e3cf2a839de060b4.png)](https://p0.ssl.qhimg.com/t01e3cf2a839de060b4.png)

其指令以***和对应指令数字组成，以下为控制指令功能列表。[![](https://p5.ssl.qhimg.com/t017012b16c12d299f1.png)](https://p5.ssl.qhimg.com/t017012b16c12d299f1.png)



## 控制基础设施

APT-C-12组织近期活动中使用的恶意代码利用了applinzi.com域名下的二级域名作为控制域名，该域名为Sina App Engine的云服务托管。[![](https://p2.ssl.qhimg.com/t0173c618c486d0b090.png)](https://p2.ssl.qhimg.com/t0173c618c486d0b090.png)

我们测试注册了SAE的账户，其默认创建应用可以免费使用十多天，并支持多种开发语言的环境部署。

[![](https://p2.ssl.qhimg.com/t01803fb899bd573026.png)](https://p2.ssl.qhimg.com/t01803fb899bd573026.png) [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t012fa19a6067ac1f9c.png)

[![](https://p5.ssl.qhimg.com/t01398703f4b808d65e.png)](https://p5.ssl.qhimg.com/t01398703f4b808d65e.png)

我们尝试对其控制服务器进行连接，但其后台处理程序已经出错，通过返回的错误信息我们可以发现该组织使用Python部署的后台应用，并使用了flask作为其Web服务实现。

[![](https://p1.ssl.qhimg.com/t01c60d92aca0721ea5.png)](https://p1.ssl.qhimg.com/t01c60d92aca0721ea5.png)

### SAE控制协议

该组织针对SAE的部署应用实现了一套访问协议，其分为put，info，get，del四个功能。

其中put用于上传文件：

[![](https://p5.ssl.qhimg.com/t01b8d0478ca46ee159.png)](https://p5.ssl.qhimg.com/t01b8d0478ca46ee159.png) [![](https://p3.ssl.qhimg.com/t017c55abe00c292537.png)](https://p3.ssl.qhimg.com/t017c55abe00c292537.png)

get用于获取文件：

[![](https://p5.ssl.qhimg.com/t018dddc64b84b1641c.png)](https://p5.ssl.qhimg.com/t018dddc64b84b1641c.png)

info用于获取信息：

[![](https://p1.ssl.qhimg.com/t01949fdd114e71e1e4.png)](https://p1.ssl.qhimg.com/t01949fdd114e71e1e4.png)

del用于删除文件：

[![](https://p0.ssl.qhimg.com/t01de63683eb42a4256.png)](https://p0.ssl.qhimg.com/t01de63683eb42a4256.png)



## 总结

继360威胁情报中心发现该组织利用Digital Ocean云服务作为命令控制和回传通信渠道以后，我们又发现该组织使用国内的云服务SAE构建其控制回传基础设施，利用这种方式一定程度上减少了攻击利用的成本，也增加了分析回溯的难度。



## IOC

crecg.applinzi.com

costbank.applinzi.com



## 参考链接

[https://sae.sina.com.cn/](https://sae.sina.com.cn/)

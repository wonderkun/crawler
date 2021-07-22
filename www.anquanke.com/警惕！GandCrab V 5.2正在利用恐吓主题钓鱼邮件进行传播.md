> 原文链接: https://www.anquanke.com//post/id/173231 


# 警惕！GandCrab V 5.2正在利用恐吓主题钓鱼邮件进行传播


                                阅读量   
                                **217342**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p0.ssl.qhimg.com/t01b880511d0efbe927.jpg)](https://p0.ssl.qhimg.com/t01b880511d0efbe927.jpg)



## 前言

近期，360威胁情报中心捕获到一起针对中文使用者的钓鱼邮件。该邮件带有一个压缩包，经分析发现，该压缩包内为最新的GandCrab 5.2勒索软件。基于该线索，360威胁情报中心对GandCrab勒索软件最新变种的IOC，攻击技术和传播方式进行分析汇总，并提出了一些解决方案，以供读者参考。



## 攻击分析

本次攻击的邮件内容如下所示

邮件标题为“你必须在3月11日下午3点向警察局报到!”

发件人邮箱为：[Jae-hyun@idabostian.com](mailto:Jae-hyun@idabostian.com)

发件人名称：Min, Gap Ryong

可见内容存在大量乱码字样，内容大致为请来警局参与调查，并附上了相关内容。

[![](https://p4.ssl.qhimg.com/t01973b2832d8ac17cf.png)](https://p4.ssl.qhimg.com/t01973b2832d8ac17cf.png)

通过解压03-11-19.rar 后，可见其内含有一个伪装成word图片的，带中文乱码的exe文件。

“你 须瞍3昱11祉 珥3锩  添筇涎报羽”

[![](https://p2.ssl.qhimg.com/t01026ac131282251ba.png)](https://p2.ssl.qhimg.com/t01026ac131282251ba.png)

运行恶意软件后，可见桌面被替换并显示GandCrab 5.2的相关勒索信息

[![](https://p4.ssl.qhimg.com/t01a0cddd1704a45e7a.png)](https://p4.ssl.qhimg.com/t01a0cddd1704a45e7a.png)

勒索信息文本，其中文本名称和后缀均为随机生成，勒索信息文本为固定格式XXXXXXX-MANUAL.txt

其中Tor 节点如下:

http://gandcrabmfe6mnef.onion/e49217da629e6a2d

[![](https://p0.ssl.qhimg.com/t0117260e8ce3da2641.png)](https://p0.ssl.qhimg.com/t0117260e8ce3da2641.png)



## 样本分析

恶意代码的入口处会先通过CreateToolHelp32Snapshot创建进程快照，然后调用Module32First判断返回值：

[![](https://p4.ssl.qhimg.com/t0104e7f94152a99d43.png)](https://p4.ssl.qhimg.com/t0104e7f94152a99d43.png)

返回值等于0的话会进入fun_ExecMain函数后会执行后续的恶意代码，在之前会填充很多垃圾指令 ，为了免杀：

[![](https://p0.ssl.qhimg.com/t01758cb4d41314f224.png)](https://p0.ssl.qhimg.com/t01758cb4d41314f224.png)

会解密文件中包含的2块数据，复制到新申请的可执行的内存空间，解密后的数据是shellcode，直接执行起来：

[![](https://p1.ssl.qhimg.com/t01c26629f7ba3e9259.png)](https://p1.ssl.qhimg.com/t01c26629f7ba3e9259.png)

解密后的2块数据合并成一个完整的shellcode，如图为解密后的数据的汇编代码：

[![](https://p4.ssl.qhimg.com/t01ce323d28f82e9275.png)](https://p4.ssl.qhimg.com/t01ce323d28f82e9275.png)

Shellcode的功能主要是解密出勒索的主体PE并在内存中加载起来:

[![](https://p0.ssl.qhimg.com/t010e4d64b6140e4079.png)](https://p0.ssl.qhimg.com/t010e4d64b6140e4079.png)

[![](https://p4.ssl.qhimg.com/t017985ac443971a95a.png)](https://p4.ssl.qhimg.com/t017985ac443971a95a.png)

Dump出解密出的PE的信息如下：

MD5:

b961adffea4c6cf915e1f04ddea6408e

编译时间：

2019-02-24 00:51:29

字符串信息：

[![](https://p3.ssl.qhimg.com/t013fca55a601653d77.png)](https://p3.ssl.qhimg.com/t013fca55a601653d77.png)

字符串用的RC4算法，所有的字符串都用了RC4算法：

[![](https://p0.ssl.qhimg.com/t01c4f7587c51fc7342.png)](https://p0.ssl.qhimg.com/t01c4f7587c51fc7342.png)

[![](https://p1.ssl.qhimg.com/t01ae12fca0652a3b01.png)](https://p1.ssl.qhimg.com/t01ae12fca0652a3b01.png)

传进去的数据结构为：

0-0x10字节：RC4密钥

Len = Dword(0x10-0x14)^dword(0x15-0x18)：后面数据的长度

0x18- Len:待解密的数据

例如下面的数据：

75 31 45 89 2A 27 CA 9B D3 65 BE CF D2 94 50 1E //RC4密钥

42 4C 17 1B //长度的异或前值 A

52 4C 17 1B //长度的异或后值 B   A异或B = 0x10 就是后面数据的长度

FC E3 01 54 2D D6 08 5A 67 43 6C A9 88 49 53 90 //数据

解密的数据如下：

[![](https://p0.ssl.qhimg.com/t014e3af6dad4727fd4.png)](https://p0.ssl.qhimg.com/t014e3af6dad4727fd4.png)

以下为勒索成功后的截图：

[![](https://p5.ssl.qhimg.com/t010ae3179f122b1e1f.png)](https://p5.ssl.qhimg.com/t010ae3179f122b1e1f.png)



## 传播方式

目前已知的传播方式如下：

1、定向鱼叉攻击邮件投放

2、垃圾邮件批量投放传播

3、网页挂马攻击

4、利用CVE-2019-7238(Nexus Repository Manager 3远程代码执行漏洞)进行传播

5、利用weblogic漏洞进行传播

6、利用自动化机制病毒进行传播([https://mp.weixin.qq.com/s/R-Ok96U5Jb2aaybUfsQtDQ](https://mp.weixin.qq.com/s/R-Ok96U5Jb2aaybUfsQtDQ))

传播方式包括:

a)通过RDP、VNC等途径进行爆破并入侵

b)利用U 盘、移动硬盘等移动介质进行传播

c)捆绑、隐藏在一些破解、激活、游戏工具中进行传播

d)感染 Web/FTP 服务器目录并进行传播

主要传播端口为： 445、135、139 、3389、5900 等端口



## 解决方案

请持续关注国内外厂商对Gandcrab 5.2的解密情况

Gandcrab 5.1之前版本的解密工具：

http://lesuobingdu.360.cn



## 防护建议

1、尽量关闭不必要的端口，如 445、135、139 等，对 3389、5900 等端口可进行白名单配置，只允许白名单内的 IP 连接登陆。

2、采用高强度的密码，避免使用弱口令密码，并定期更换密码。

3、安装 360 天擎新一代终端安全管理系统。

4、及时更新软件，安装补丁。



## 总结

由于Gandcrab 5.2版本会通过垃圾电子邮件分发，因此我们建议您不要打开任何未知来源的电子邮件，尤其是不要打开附件。即使附件来自常用联系人，我们也建议您在打开之前，使用360天擎对其进行扫描，以确保它不包含任何恶意文档或文件。

360威胁情报中心最后再次提醒各企业用户，加强员工的安全意识培训是企业信息安全建设中最重要的一环，如有需要，企业用户可以建设态势感知，完善资产管理及持续监控能力，并积极引入威胁情报，以尽可能防御此类攻击。

目前，基于360威胁情报中心的威胁情报数据的全线产品，包括360威胁情报平台（TIP）、天眼高级威胁检测系统、360 NGSOC等，都已经支持对Gandcrab 5.2的检测。



## IOCs

下面为近期Gandcrab 5.2 的IOC信息，以供参考。

d5ad7b954eace2f26a37c5b9faaf0e53

445dd888ed51e331fdcf2fa89199cca6

9b1305f5a007bbcf285728d708b244bd

0fa03c293462822f60a3ebb1a156e01c

a092fd3cf6da1885ff348b3c6d1fd922

e17a131aa1ea229a176459547c7e7a3f

f2b4239309bc461e844091814ce3cb9c

f6fffc29f5ec5e8e94e130739fad8da1

ad18697ef19bb91a98e5778555fb41c5

5363d5f1769bc5cfdd9484c9025beb1b

c7b236f53ad4360c6934c263fe882f5e

1aafc253fa9fe127f695e609c44c4db8

fa507fd54405ca99625d0afdb18a7aff

fa720701a8c8b07908202e382782ab7a

ac6df351b6516f22aec3d59caa0c5d6a

608a8be96683d0bc308a1abdb18844c3

6937f4e49a1f57b0e0f223a71235d66e

b2e8b64ff69edda0db78987048a686e2

e376c7ab4f38eb1c1ed151d9530f1243

8d690776b198c1b65ec038d1a31a77b4

23f14288b9744bb32040d533b7198b93

### 传播恶意软件的下载链接

[http://104.248.43.245/audi.exe](http://104.248.43.245/audi.exe)

[http://92.63.197.153/kg.exe](http://92.63.197.153/kg.exe)

[http://92.63.197.153/k.exe](http://92.63.197.153/k.exe)

[http://101.96.10.37/92.63.197.153/work/1.exe](http://101.96.10.37/92.63.197.153/work/1.exe)

http://159.89.142.248/wow.exe

### Tor节点

http://gandcrabmfe6mnef.onion/e49217da629e6a2d

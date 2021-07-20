> 原文链接: https://www.anquanke.com//post/id/180864 


# 深入分析Ewon Flexy物联网路由器（下）


                                阅读量   
                                **189489**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者pentestpartners，文章来源：pentestpartners.com
                                <br>原文地址：[https://www.pentestpartners.com/security-blog/ewon-flexy-iot-router-a-deep-dive/](https://www.pentestpartners.com/security-blog/ewon-flexy-iot-router-a-deep-dive/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01c5aee73101c0f4f0.png)](https://p5.ssl.qhimg.com/t01c5aee73101c0f4f0.png)





## 0x0B 逆向分析Ewon文件

根据之前的截图，我们无法在NAND Flash转储文件中找到太多信息。我希望系统会使用预设的工具（如apache2、lighthttpd或者nginx）来设置web接口，或者使用vsftpd及其他解决方案来设置FTP服务。幸运的是，当开发者决定使用自己定制的服务版本时，可能会忽略掉许多安全功能或者保护措施。

逆向分析二进制文件时，我们很自然就会搜索其中包含的字符串。

我在文件中简单`grep`搜索某些字符串，比如`password`、`pass`以及`private`，回头我们再来分析搜索出的结果。

[![](https://p5.ssl.qhimg.com/t0161ef713fdab81348.png)](https://p5.ssl.qhimg.com/t0161ef713fdab81348.png)

[![](https://p5.ssl.qhimg.com/t015b79d83494d452b2.png)](https://p5.ssl.qhimg.com/t015b79d83494d452b2.png)

利用IDA Pro分析二进制文件，获取反汇编代码。结果并不是特别完美，但至少能给出一些信息。

[![](https://p5.ssl.qhimg.com/t01fa173b5f92eb2715.png)](https://p5.ssl.qhimg.com/t01fa173b5f92eb2715.png)

首先我想澄清的就是配置文件中加密存储的值（VPN秘钥、密码）。

一番搜索后，我找到了一个函数：`cfgcrypt_DecryptCfgStr`。

该函数在IDA中的布局图如下：

[![](https://p4.ssl.qhimg.com/t0136b1470f62a5be79.png)](https://p4.ssl.qhimg.com/t0136b1470f62a5be79.png)

详细布局如下：

[![](https://p3.ssl.qhimg.com/t01351e30af284f2271.png)](https://p3.ssl.qhimg.com/t01351e30af284f2271.png)

在Dave小伙伴（人形自走反汇编器）的帮助下，我们发现`#_1_`可以表示正在使用的是什么加密算法。

此外，在Ewon的`comcfg.txt`文件中有一项设置：`CryptMode:1`，刚好与我们的判断相符。

[![](https://p1.ssl.qhimg.com/t0170fab00b81e937af.png)](https://p1.ssl.qhimg.com/t0170fab00b81e937af.png)

此时我们还没有看到配置文件中有其他可变值，但相信我们的研究方向没有问题，因为Ewon二进制文件中硬编码了许多相同的秘钥及IV（初始向量）。

如果`CryptModd`设置`&gt;2`的值，那么函数就会输出错误消息，将这个值设置为`0`。

[![](https://p0.ssl.qhimg.com/t0123ce03695b5db0bb.png)](https://p0.ssl.qhimg.com/t0123ce03695b5db0bb.png)

我认为如果是`#_0_`，那么设备就会使用`blowfish`加密算法，我们也拿到了算法所使用的秘钥及IV，然而这里设备使用的是`#_1_`。

那么`#_1_`的具体代表的是什么？

固件中有个`cfgcrypt_CheckCryptmode`函数，该函数会检查加密字符串的头部，根据头部值返回一个结果值。

[![](https://p4.ssl.qhimg.com/t01cb79ad3c461b2d20.png)](https://p4.ssl.qhimg.com/t01cb79ad3c461b2d20.png)

然而设备永远不会调用这个函数，这一点比较奇怪，但`cfgcrypt_DecryptCfgStr`函数中有一个相似的代码结构。

[![](https://p4.ssl.qhimg.com/t01f796b90a5fddf821.png)](https://p4.ssl.qhimg.com/t01f796b90a5fddf821.png)

似乎设备会在多个地方复用代码。

最终所有的加密及解密函数都会汇聚到`ctr_encrypt`函数。

[![](https://p1.ssl.qhimg.com/t01bf7747767964cf42.png)](https://p1.ssl.qhimg.com/t01bf7747767964cf42.png)

`ctr_decrypt`函数代码如下：

[![](https://p3.ssl.qhimg.com/t01a2f985c9136ccefb.png)](https://p3.ssl.qhimg.com/t01a2f985c9136ccefb.png)

这里我不会讨论具体细节，只需要知道`ctr_encrypt`代码中包含一个XOR函数。



## 0x0C 逆向分析固件

一开始我就被固件困住了脚步，我们可以从Ewon官网上下载到这个 固件：

[![](https://p4.ssl.qhimg.com/t01d1dd121b69795763.png)](https://p4.ssl.qhimg.com/t01d1dd121b69795763.png)

当想详细分析固件时，我们发现固件经过加密处理：

[![](https://p1.ssl.qhimg.com/t0174092a024760ec9b.png)](https://p1.ssl.qhimg.com/t0174092a024760ec9b.png)

文件头部较为清晰，包含版本号、发布时间等都以明文表示，但后面就是一些看不懂的数据。

因此回到Ewon二进制文件，查找引用了固件文件名的部分数据。

首先我们可以找到对SD卡的引用：

[![](https://p1.ssl.qhimg.com/t01e65bef62957f5c3a.png)](https://p1.ssl.qhimg.com/t01e65bef62957f5c3a.png)

因此，如果SD卡上存在固件，那么设备就会尝试更新。这一点非常正常，然而根据用户文档，我们可以将`ewonfwr.ed`文件上传到FTP（如果通过身份认证的话），随后Ewon就会根据需要处理固件。

我在固件文件中搜索满足这些处理逻辑的内容，最终找到了一个函数：`loem_UncryptFile`。该函数似乎会打开一个文件，然后调用解密函数。

[![](https://p0.ssl.qhimg.com/t015a32ee11cd90503b.png)](https://p0.ssl.qhimg.com/t015a32ee11cd90503b.png)

Ewon程序会检查固件文件是否已上传到ftp服务器或者SD卡中，加载manifest信息（检查固件版本、日期等），然后解密固件文件及数据。

[![](https://p5.ssl.qhimg.com/t014e17824d3c736c32.png)](https://p5.ssl.qhimg.com/t014e17824d3c736c32.png)

固件加密基于Blowfish算法（程序中大量引用了这个算法），并且程序中硬编码了加密秘钥。

[![](https://p4.ssl.qhimg.com/t0134c404450eff5245.png)](https://p4.ssl.qhimg.com/t0134c404450eff5245.png)

非常棒，那么我们再次回到固件文件。

查看数据后，我判断加密数据从`0x0140h`开始，直到文件结尾。将这部分内容拷贝出来，尝试使用程序内置的秘钥进行解密。

[![](https://p2.ssl.qhimg.com/t01ed0e1f5455a35fee.png)](https://p2.ssl.qhimg.com/t01ed0e1f5455a35fee.png)

[![](https://p0.ssl.qhimg.com/t01cec4c56752b26bf4.png)](https://p0.ssl.qhimg.com/t01cec4c56752b26bf4.png)

我们的确能解出一些数据，但似乎只能解密一半数据，这一点非常奇怪，但至少我们的方向没有错。

回到二进制程序中，似乎程序会使用这个IV，在升级前备份固件，那么这个IV究竟在哪？

Dave又站了出来，提示我如果这个值不在程序中，那么很有可能在固件中，这一点非常正常。

再次回到固件上，查找头部数据。我们来寻找可以使用的8bit据流。删除加密后的无关信息后，我们留下了一部分数据，比较明显的8bit数据流就位于数据末尾（下图高亮部分）：

[![](https://p3.ssl.qhimg.com/t014754b404e158ddca.png)](https://p3.ssl.qhimg.com/t014754b404e158ddca.png)

将这个值输入python脚本中，观察运行结果：

[![](https://p5.ssl.qhimg.com/t01d3ba28fc1b2630c7.png)](https://p5.ssl.qhimg.com/t01d3ba28fc1b2630c7.png)

现在我们终于解出完整数据。

来观察文件系统，特别是`update.sh`文件：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01cc65d43a2e96c26f.png)

这里似乎出现了很多文件，但实际上只是NAND Flash转储数据中Ewon的`/opt`目录，因此这里并没有什么新的信息。

再来观察`update.sh`：

[![](https://p5.ssl.qhimg.com/t01e2a2f9abdc3e53e5.png)](https://p5.ssl.qhimg.com/t01e2a2f9abdc3e53e5.png)

非常好，来具体看一下程序的处理逻辑，能否找到有趣的点：

[![](https://p1.ssl.qhimg.com/t01246bfbb01539b76b.png)](https://p1.ssl.qhimg.com/t01246bfbb01539b76b.png)

我看到可能存在命令执行点！

我修改了`update.sh`，重新生成固件，然后设置成高版本后重新上传该固件：

[![](https://p0.ssl.qhimg.com/t01a140acc176fda114.png)](https://p0.ssl.qhimg.com/t01a140acc176fda114.png)

令人失望的是，这种方法无法奏效。似乎设备会对该文件执行CRC校验，因为我们在Ewon日志中找到了“riftp-Invalid checksum”错误：

[![](https://p4.ssl.qhimg.com/t01ba7ecabc642063a8.png)](https://p4.ssl.qhimg.com/t01ba7ecabc642063a8.png)

再次回到程序逻辑上来：

[![](https://p2.ssl.qhimg.com/t01f4823d0e9b63c491.png)](https://p2.ssl.qhimg.com/t01f4823d0e9b63c491.png)

这里包含一个CRC16x2校验。我不能百分版确定校验针对的是固件的加密数据，还是针对加密前的squashfs数据。

来对比两个固件版本。我将两个文件中共同的部分设置为相同值，以减少文件存在的差异：

[![](https://p1.ssl.qhimg.com/t01e96fdf18f6877ddc.png)](https://p1.ssl.qhimg.com/t01e96fdf18f6877ddc.png)

上图中红色部分数据就是头部中存在差异的数据。

进一步分析后，我看到两个文件中红色区域仍有一些相似性：

[![](https://p3.ssl.qhimg.com/t012a1433c70c49c3ec.png)](https://p3.ssl.qhimg.com/t012a1433c70c49c3ec.png)

在固件文件的加密数据上执行一些CRC校验操作，看我们能否在头部中找到相关的信息：

```
Ver 13_2s1 = 8.433 mb (Latest)

CRC16 (encrypted blob) = AF3C

CRC32 (encrypted blob) = F388096F

Ver 13_0s0 = 12,589 mb (Not Latest)

CRC16 (encrypted blob) = A65D

CRC32 (encrypted blob) = 259BC946
```

似乎有所收获！

[![](https://p5.ssl.qhimg.com/t0159527e60102cebb5.png)](https://p5.ssl.qhimg.com/t0159527e60102cebb5.png)

这正是加密数据对应的CRC32值！正是在头部文件中！在`0x00B0`处！我们来稍微修改一下，看一下改动后的校验结果：

[![](https://p2.ssl.qhimg.com/t01cefa9b28ced4651c.png)](https://p2.ssl.qhimg.com/t01cefa9b28ced4651c.png)

好吧，还是有些地方不对。

让我们再次回到Ewon程序中。当在程序中搜索时，我发现有个函数会涉及到一些头部数据：

[![](https://p0.ssl.qhimg.com/t01f7206ef3e127dd7c.png)](https://p0.ssl.qhimg.com/t01f7206ef3e127dd7c.png)

这里`riftp_EDFHeaderPtr`是固件文件的开头处，因此为`0`。

在144行，代码会比较`rfiftp_EDFHeaderPtr + 16`的值，判断这个值是否等于`v10`（CRC16 x 2校验值）。

[![](https://p1.ssl.qhimg.com/t01f11dcd9353f91beb.png)](https://p1.ssl.qhimg.com/t01f11dcd9353f91beb.png)

比较困惑我（和其他小伙伴）的一个点就是CRC校验函数。从二进制代码中，我们知道（或者至少认为）程序正在计算加密数据块的CRC16x2校验值，但具体计算逻辑如下：

[![](https://p0.ssl.qhimg.com/t01f7849d03ebd97a14.png)](https://p0.ssl.qhimg.com/t01f7849d03ebd97a14.png)

Dave和我决定重新CRC16x2函数，看一下能得到什么结果：

[![](https://p5.ssl.qhimg.com/t01d1f46d1cb21d306f.png)](https://p5.ssl.qhimg.com/t01d1f46d1cb21d306f.png)

虽然我们得到的结果不大一样，但我们认为已经非常接近事实真相了。

此外我们还对固件文件进行暴力尝试，想看看是否有任何数据与头部中存储的值相匹配：

[![](https://p5.ssl.qhimg.com/t01067fb6a5cb623907.png)](https://p5.ssl.qhimg.com/t01067fb6a5cb623907.png)

不幸的是，这也是我们研究的终点，不能再进一步。

我们尝试了各种不同的CRC16校验方法，不同的xor位等，但得不到更进一步的结果，无法匹配`0xA8`处的值。

这个过程中我们使用了[pycrc](https://pycrc.org/models.html)，这款工具非常强大，帮我们省了不少功夫。



## 0x0D 披露时间线

2019-01-29 首次联系Ewon反馈漏洞

2019-02-04 官方确认漏洞并预估处理时间节点

2019-02-11 PTP与Ewon都认为处理周期有点长

2019-05-23 在最终披露前进行协商

2019-05-28 Ewon反馈并提供测试固件

2019-06-04 Ewon披露相关公告

2019-06-18 PTP披露相关公告，现在大家可以在[此处](https://websupport.ewon.biz/support/product/manual-firmware-update/manual-firmware-download)下载更新版的FW 13.3s0

我们在2019年1月29日向EWon Flexy的制造商HMS Networks报告了相关情况。整个过程略微曲折，但最终官方确认并修复了漏洞，这里不再赘述。



## 0x0E 缓解措施及建议

### <a class="reference-link" name="%E7%94%A8%E6%88%B7%E8%A7%92%E5%BA%A6"></a>用户角度

不要将Ewon Flexy（或者任何ICS设备）放在公开互联网中，这会引来不必要的麻烦。

记得修改默认凭据。

分段规划IT及OT网络，部署适当的访问控制机制。

### <a class="reference-link" name="%E5%8E%82%E5%95%86%E8%A7%92%E5%BA%A6"></a>厂商角度

HMS有一个安全远程访问解决方案：[Talk2M](https://www.ewon.biz/cloud-services/talk2m)，应该能缓解这个问题。

我们还没测试过Talk2M，无法发表关于安全性方面的意见，但添加一个防御层始终不算坏事。有空时我会分析一下新的固件。

修复bug后的新固件可从[此处](https://websupport.ewon.biz/support/product/download-firmware/ewon-firmware-0)下载。

### <a class="reference-link" name="%E6%88%91%E4%BB%AC%E7%9A%84%E5%BB%BA%E8%AE%AE"></a>我们的建议

更新Ewon Flexy固件，升级到最新版。

同时记得更新所有的工控系统。如果无法更新ICS（版本太老、官方不再支持或者过于关键无法改动），可以考虑针对性部署额外的安全控制机制。



## 0x0F 总结

我不想草草结束这篇文章，回头我会发表第二篇分析文章。

整个研究过程比较曲折，我个人也学到了许多知识。现在我非常喜欢IDA，但我使用Ghidra的次数越来越多（这是款免费产品，某些地方更加方便）。

Ewon Flexy是一款非常不错的设备，这个研究过程也是我自己想看一下我的能力范围，还有哪些地方需要提高等。

如果我成功构造出能够正常工作的固件，那么后续会有更多研究成果可以公布。

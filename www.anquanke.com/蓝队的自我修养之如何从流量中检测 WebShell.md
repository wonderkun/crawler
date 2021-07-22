> 原文链接: https://www.anquanke.com//post/id/238341 


# 蓝队的自我修养之如何从流量中检测 WebShell


                                阅读量   
                                **199799**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t011dde4ccb9a1d9297.jpg)](https://p1.ssl.qhimg.com/t011dde4ccb9a1d9297.jpg)



## 背景

众所周知，攻防演练过程中，攻击队入侵企业网站时，通常要通过各种方式获取 webshell，从而获得企业网站的控制权，然后方便实施之后的入侵行为。在冰蝎、哥斯拉这类加密型 webshell 工具出现之前，中国菜刀、蚁剑这类工具常被攻击队使用，与菜刀和蚁剑不同，冰蝎和哥斯拉使用加密隧道传输数据，不易被安全设备发现，同时，无文件内存 webshell 的兴起，给检测带来了更大的压力。因此，对这类加密型 webshell 和无文件内存 webshell 的检测是非常有必要的。

## 难点

当前，这类加密型 webshell 检测存在以下难点：
1. 使用加密隧道传输数据，无明文通讯特征。
1. 内存 webshell 无文件落地。
## 目标

通过攻防演练的实践，总结一套关于加密 webshell 和内存 webshell 的检测方法，分析和总结该类 webshell 通讯特征，通过流量及时准确的发现主机失情况，及时处理。

## 方法论

当出现一个新型 webshell 工具时，我们可以通过如下几个方面总结相关特征，从而实现相关检测。

[![](https://p0.ssl.qhimg.com/t01f7bc0274a0b1052f.png)](https://p0.ssl.qhimg.com/t01f7bc0274a0b1052f.png)
1. webshell 样本：分析 webshell 的执行逻辑，提取 webshell 执行过程中必须存在的函数、参数，对该类 webshell 实现上传、写入的检测。
1. 通讯过程中必存在参数：分析 webshell 服务端和客户端，提取因实现问题而在交互过程中必须存在的参数。
1. 加密算法特征：分析该 webshell 通讯过程中的加密方法，获取该加密方法生成的密文所在集合。
1. 工具本身 bug：因为工具是人力开发的，难以避免会存在一些 bug，这些 bug 可以成为识别该类工具的特征。
1. 与正常业务不符：分析通讯过程中，该 webshell 和正常业务的不同，可以粗略的筛选出可能异常的通讯。
## 案例

我们将从以上方法论总结的几种方法，举例说明如何提取特征。

### **上传样本**

可以通过对上传的样本进行检测，从而发现威胁。我们可以通过分析这类 webshell 工具的源码，提取生成的 webshell 的特征，从而实现检测。以下以哥斯拉为例，可以看到其生成 webshell 时导入一个模板，根据模板生成相应的 webshell，所以我们总结生成模板的特征，即可对这类上传行为进行准确的检测。

[![](https://p2.ssl.qhimg.com/t01d3d6564f461a8262.png)](https://p2.ssl.qhimg.com/t01d3d6564f461a8262.png)

### **通讯过程中必存在参数**

在冰蝎 3.0 的服务端，是通过如下代码读取 post 请求。

代码的意思是，直接读取 post 请求中 body 的内容。所以请求的 http 中，content-type 一定为 application/octet-stream。否则就会出现非预期 http 编码的情况。这类特征属于通讯过程中必存在参数，可以通过这类特征的组合，对相关 webshell 通讯进行检测（这里仅做举例，这类检测肯定为多特征结合）。

### **加密方法存在的一些弱特征**

冰蝎通讯时，会建立加密通讯隧道，主要请求体和返回体内容有如下三种情况：
<td class="ql-align-center" data-row="1">**请求体加密方式**</td><td class="ql-align-center" data-row="1">**返回体加密方式**</td>
<td class="ql-align-center" data-row="2">AES 后 Base64</td><td class="ql-align-center" data-row="2">AES 后 Base64</td>
<td class="ql-align-center" data-row="3">AES 后 Base64</td><td class="ql-align-center" data-row="3">AES</td>
<td class="ql-align-center" data-row="4">AES</td><td class="ql-align-center" data-row="4">AES</td>

对于 AES 后 Base64 加密，其加密后所有值落在 [a-zA-Z0-9+\=]，很容易通过正则去覆盖。

对于 AES 加密，其加密后的值无 Base64 中相关特征，但是，可以明显看出，密文内容中不可见字符明显增多。可以通过不可见字符进行检测，从而覆盖对 AES 这类加密后的请求体或返回体的识别。

[![](https://p1.ssl.qhimg.com/t015157175107b32863.png)](https://p1.ssl.qhimg.com/t015157175107b32863.png)

这类仅为一些弱特征，仅举例说明，需要多特征组合，才能实现准确的检测。

### **工具本身的 bug**

这类工具都是人力开发的，难免存在一些 bug，我们可以通过找到这些 bug，从而在流量中识别出该类工具。

如在冰蝎某一版本中，php 相关 webshell 通讯在一个 http 请求报文中存在两个 PHPSESSID，这属于工具的 bug，可以通过该 bug 以及其他一些特征，识别出该工具。

[![](https://p5.ssl.qhimg.com/t01dd5576cf9fb68d95.png)](https://p5.ssl.qhimg.com/t01dd5576cf9fb68d95.png)

### **与正常业务不符**

对于无文件内存 webshell，攻击者为了隐藏攻击行为，将注入 webshell 的路径选为静态文件路径，如 jpg、ico、png 等，但这样就会存在一些异于正常的行为，如请求静态文件返回内容不同、带请求体请求静态文件等。以下为一个冰蝎内存 webshell 的示例。

[![](https://p0.ssl.qhimg.com/t01de8f454039a86835.png)](https://p0.ssl.qhimg.com/t01de8f454039a86835.png)

## 总结

在本文中，我们总结了从流量中寻找加密型 webshell 和无文件内存 webshell 的特征方法，分别是：
1. webshell 样本
1. 通讯过程中必存在参数
1. 加密方法特征
1. 工具本身的 bug
1. 与正常业务不符
在实战测试中，通过上述几点，对加密型 webshell 和无文件内存 webshell 的通讯流量进行分析，总结相关弱特征和强特征，多种特征结合，可以准确识别这类 webshell 的通讯过程，及时处置和发现失陷主机。

> 原文链接: https://www.anquanke.com//post/id/92223 


# 360CERT：利用WebLogic漏洞挖矿事件分析


                                阅读量   
                                **365870**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t014c657c2b0da40ab1.jpg)](https://p4.ssl.qhimg.com/t014c657c2b0da40ab1.jpg)



## 0x00 事件背景

近日，360攻防实验室（360ADLab）共享了一份“黑客利用Oracle WebLogic漏洞攻击”的威胁情报，攻击者疑似利用CVE-2017-3506/CVE-2017-10352漏洞进行加载恶意程序进行门罗币挖矿攻击。

360ADLab和360CERT对此次事件进行了技术分析。

鉴于该漏洞可直接远程获取目标系统权限和虚拟货币的明显增值，建议相关企业尽快进行安全评估。



## 0x01 WebLogic相关漏洞分析

根据目前的信息分析，攻击者使用的漏洞为Oracle WebLogic已修复的漏洞CVE-2017-3506/CVE-2017-10352。

该类型漏洞攻击方式比较简单，攻击者通过特殊构造的HTTP包就能获取目标系统权限，且该漏洞影响到Linux和Windows等平台下的WebLogic服务。

### 分析环境

[![](https://p3.ssl.qhimg.com/t011aa9d43257f95480.png)](https://p3.ssl.qhimg.com/t011aa9d43257f95480.png)

### 技术细节

分析人员在使用已公开的WebLogic攻击代码测试后，根据返回包异常信息中的调用栈可以知道会进入到WorkContextXmlInputAdapter类中的readUTF方法中去：

[![](https://p2.ssl.qhimg.com/dm/1024_547_/t01ea655078c97d1b1d.png)](https://p2.ssl.qhimg.com/dm/1024_547_/t01ea655078c97d1b1d.png)

WorkContextXmlInputAdapter类其中一部分：

[![](https://p4.ssl.qhimg.com/dm/1024_772_/t019d845e45e45b602c.png)](https://p4.ssl.qhimg.com/dm/1024_772_/t019d845e45e45b602c.png)

在这里是会使用XMLDecoder来进行反序列化的。通过下断点远程调试来观察其具体流程：

[![](https://p3.ssl.qhimg.com/dm/1024_546_/t012578eebaa34ec8ff.png)](https://p3.ssl.qhimg.com/dm/1024_546_/t012578eebaa34ec8ff.png)

可以看到攻击代码中构造好的数据直接进入到了XMLDecoder类的readObject方法中，接下来的便是获取对象类型，参数和执行方法的反序列化过程。攻击代码中使用ProcessBuilder来实现远程命令执行。针对这个地方的漏洞，weblogic在4月份是发布了补丁的。下面是WorkContextXmlInputAdapter类源代码和4月份补丁的对比：

[![](https://p3.ssl.qhimg.com/dm/1024_499_/t010d4c98c6f1b7f865.png)](https://p3.ssl.qhimg.com/dm/1024_499_/t010d4c98c6f1b7f865.png)

可以明显看到添加了一个validate方法来对输入流进行校验，但是该校验方法是非常简单的，通过获取标签名来检测是否有object标签的出现，要是出现了object标签便抛出异常来终止执行流程。但是这个检测方法是非常不严谨的，在不使用object标签的情况下一样是可以利用的。利用演示：

[![](https://p5.ssl.qhimg.com/dm/1024_340_/t01663006938d2cb512.png)](https://p5.ssl.qhimg.com/dm/1024_340_/t01663006938d2cb512.png)

最后看下10月份的补丁：

[![](https://p4.ssl.qhimg.com/dm/1024_467_/t01e2b653cfd08a1471.png)](https://p4.ssl.qhimg.com/dm/1024_467_/t01e2b653cfd08a1471.png)

相对于4月份的补丁来说添加了更多对于其它标签的检测，只有打了10月份的补丁这个漏洞才能真正被补上。



## 0x02 攻击流程

攻击者通过预先收集包括Windows和Linux平台的WebLogic目标主机（实际上不仅仅是WebLogic漏洞），再通过CVE-2017-3506/CVE-2017-10352对目标主机植入挖矿程序，包括Carbon/xmrig, , Claymore-XMR-CPU-Miner等。该攻击行为会造成目标主机CPU资源耗尽等风险。

根据对45[.]123[.]190[.]178等一系列C2里存活样本的分析，攻击者整体上会进行如下攻击流程：

1. 通过WebLogic等漏洞植入对应恶意代码。

[![](https://p3.ssl.qhimg.com/t01e0f969b2a5bb3307.png)](https://p3.ssl.qhimg.com/t01e0f969b2a5bb3307.png)

2. 攻击时会适配对应系统：

a) Windows通过PowerShell脚本，win.txt。

b) Linux平台通过Shell脚本，lin.txt。

3. 具体会执行如下挖矿操作（疑似xmrig）：

a) 创建挖矿进程

b) 注册矿机信息

c) 存活性监测

### 相关技术信息

1. 攻击者挖矿xmrig，github地址为：

```
https[:]//github.com/xmrig/xmrig
```

2. 相关PowerShell脚本

```
[ http://C2/win.txt]
```

[![](https://p4.ssl.qhimg.com/t01f1c4a115beed3542.png)](https://p4.ssl.qhimg.com/t01f1c4a115beed3542.png)

3. 相关Shell脚本

```
[ http://C2/lin.txt]
```

[![](https://p1.ssl.qhimg.com/dm/1024_888_/t01ccd66dee9a122d6e.png)](https://p1.ssl.qhimg.com/dm/1024_888_/t01ccd66dee9a122d6e.png)

4. 运行状态

[![](https://p2.ssl.qhimg.com/t0165fc281f73cf9138.png)](https://p2.ssl.qhimg.com/t0165fc281f73cf9138.png)

5. 部分文件组成

[![](https://p3.ssl.qhimg.com/t0100ed65faac3e094f.png)](https://p3.ssl.qhimg.com/t0100ed65faac3e094f.png)

6. 帐号相关信息

```
42HrCwmHSVyJSAQwn6Lifc3WWAWN56U8s2qAbm6BAagW6Ryh8JgWq8Q1JbZ8nXdcFVgnmAM3q86cm5y9xfmvV1ap6qVvmPe
4BrL51JCc9NGQ71kWhnYoDRffsDZy7m1HUU7MRU4nUMXAHNFBEJhkTZV9HdaL4gfuNBxLPc3BeMkLGaPbF5vWtANQt989KEfGRt6Ww2Xg8
```

7. 疑似被黑网站，用作C2

[![](https://p3.ssl.qhimg.com/t01faff064908456e9d.png)](https://p3.ssl.qhimg.com/t01faff064908456e9d.png)

### IoCs

域名/IP

45[.]123[.]190[.]178

69[.]165[.]65[.]252

www.letsweb.000webhostapp.com



## 0x03 安全建议

360ADLab和360CERT建议受该漏洞影响的用户，及时更新相关补丁。

[![](https://p1.ssl.qhimg.com/t01fd75c93fa2f9fbc6.png)](https://p1.ssl.qhimg.com/t01fd75c93fa2f9fbc6.png)





## 0x04 时间线

2017-04-24 CVE-2017-3506披露<br>
2017-10-19 CVE-2017-10352披露<br>
2017-12-20 360ADLab提供威胁情报<br>
2017-12-22 360ADLab 和360CERT对事件进行分析

## 0x05 参考

1. 关于近期发生的利用weblogic漏洞进行挖矿事件的漏洞简要分析<br>
https://www.anquanke.com/post/id/92003

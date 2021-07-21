> 原文链接: https://www.anquanke.com//post/id/215169 


# 七夕—一例海莲花（OceanLotus）的恶意样本分析


                                阅读量   
                                **137089**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t010e4189ffe1a6057f.jpg)](https://p5.ssl.qhimg.com/t010e4189ffe1a6057f.jpg)



## 0x00 前⾔

在做恶意样本分析的时候，一旦涉及到APT，那必然会有一个老生常谈的名字：海莲花。

海莲花，也被称为APT32、OceanLotus。

海莲花是最早由360天眼团队，也就是现在的奇安信红雨滴团队发现并命名的。一个疑似拥有越南政治背景的APT组织。 关于海莲花，网上有比较多的分析报告，但是由于篇幅的原因，大部分报告中往往只会呈现一些关键的部分。

笔者之前在学习海莲花的时候，收集了不少相关的样本，在这里选了一个比较有代表性的分享给大家。主要是分析他们的一个代码实现。



## 0x01 海莲花公开情报

根据一些公开的情报，笔者之前做了一个关于海莲花的组织的思维导图，大概如下：

[![](https://p4.ssl.qhimg.com/t0115e8c5f6cfc8e270.png)](https://p4.ssl.qhimg.com/t0115e8c5f6cfc8e270.png)



## 0x02 样本背景

样本MD5为：3c3b2cc9ff5d7030fb01496510ac75f2

VT连接如下：[https://www.virustotal.com/gui/file/26c38d42cb6db73cbaa27217ba72c9fde19a2253ea37734ff6154a766cee4716/detection](https://www.virustotal.com/gui/file/26c38d42cb6db73cbaa27217ba72c9fde19a2253ea37734ff6154a766cee4716/detection)

app.any.run连接如下：[https://app.any.run/tasks/3220d853-72d1-41ce-ae3c-75f043aba055/](https://app.any.run/tasks/3220d853-72d1-41ce-ae3c-75f043aba055/)

[![](https://p3.ssl.qhimg.com/t01e42999ab66b68ed0.png)](https://p3.ssl.qhimg.com/t01e42999ab66b68ed0.png)

根据app.any.run可以看到，样本原始的上传名称为：

定-关于报送2019年度经营业绩考核目标建议材料的报告.doc

根据这个名字，我们无法推算出具体的攻击目标的，但是可以看到，海莲花组织的中文能力和诱饵构建能力还是在线的。



## 0x03 样本基本信息

样本伪装为正常的⽂档⽂件进⾏投递，实际上是⼀个包含⽽恶意宏代码的攻击⽂档，⽂档打开之后会仿冒<br>
杀软公司提示⽤户启⽤宏，仿冒国内安全⼚商是为了降低⽤户的警惕性，提升攻击成功率。

[![](https://p3.ssl.qhimg.com/t016e64d71c4595c58a.png)](https://p3.ssl.qhimg.com/t016e64d71c4595c58a.png)



## 0x04 宏代码分析

打开宏代码窗⼝，可以看到宏代码带有轻微混淆，⼊⼝点在AutoOpen():

[![](https://p5.ssl.qhimg.com/t011ac7acc3ccb76579.png)](https://p5.ssl.qhimg.com/t011ac7acc3ccb76579.png)

重新启动⾃身：

[![](https://p2.ssl.qhimg.com/t01122d62dfc21fbaab.png)](https://p2.ssl.qhimg.com/t01122d62dfc21fbaab.png)

宏代码运⾏后，⾸先会在%temp%⽬录下释放⼀个&lt;~$doc-ad9b812a-88b2-454c-989f7bb5fe98717e.ole&gt;⽂件，根据后⾯通过regser32.exe调⽤该ole可以得知，该ole实际上应该是个PEDLL<br>
⽂件。

[![](https://p2.ssl.qhimg.com/t01870da79cc6603fe1.png)](https://p2.ssl.qhimg.com/t01870da79cc6603fe1.png)

加载执⾏dll的同时，样本会打开%temp%⽬录下释放的File-aff94b08-6d9f-48c5-9900-<br>
5bee8ef5ab33.docx⽂件。

File-aff94b08-6d9f-48c5-9900-5bee8ef5ab33.docx是模糊⽂档⽤于迷惑受害者，⽂档内容如下：

[![](https://p2.ssl.qhimg.com/t01e3af848bb3937ca6.png)](https://p2.ssl.qhimg.com/t01e3af848bb3937ca6.png)

⽽真正的恶意⽂件~$doc-ad9b812a-88b2-454c-989f-7bb5fe98717e.ole（通过regsvr32加载的dll⽂件）已<br>
在后台悄悄运⾏，控制受害者主机。



## 0x05 释放dll分析

使⽤exeinfo可以看到该ole文件是vc系列编译器编译的标准dll⽂件。

[![](https://p1.ssl.qhimg.com/t01d784a0d6455b2d5a.png)](https://p1.ssl.qhimg.com/t01d784a0d6455b2d5a.png)

### <a class="reference-link" name="%E8%BF%90%E2%BE%8F%E7%8E%AF%E5%A2%83%E6%A3%80%E6%9F%A5"></a>运⾏环境检查

使⽤IDA加载该DLL⽂件，可以看到有如下的导出函数：

[![](https://p0.ssl.qhimg.com/t015652363385801254.png)](https://p0.ssl.qhimg.com/t015652363385801254.png)

于是定位到DLLInstall函数：

[![](https://p5.ssl.qhimg.com/t014042a4e442ab97bc.png)](https://p5.ssl.qhimg.com/t014042a4e442ab97bc.png)

dllinstall函数⾸先是通过lstrcat函数拼接了多个特殊处理过的字符串。

接着程序通过GetEnvironmentVariableW获取指定的环境变量：

[![](https://p0.ssl.qhimg.com/t01c930f50de39cf05b.png)](https://p0.ssl.qhimg.com/t01c930f50de39cf05b.png)

由于eax的值来源于[ebp-198h]，这⾥静态不太⽅便观察，于是可以在调试器中进⾏观察。使⽤x32dbg加<br>
载该dll之后，跳转到dllinstall函数的起始位置设置为新的eip：

[![](https://p4.ssl.qhimg.com/t013e380399cf76b246.png)](https://p4.ssl.qhimg.com/t013e380399cf76b246.png)

这⾥可以很清楚的看到，程序在此处尝试获取N92KG7KSpA21lGd2OPZA7QwZv这个环境变量。

[![](https://p1.ssl.qhimg.com/t01f1d5b5fd463615a9.png)](https://p1.ssl.qhimg.com/t01f1d5b5fd463615a9.png)

如果获取成功，则会跳转到下⾯去call sub_10001270，然后call eax进关键功能。

[![](https://p1.ssl.qhimg.com/t011ebb6ebc6f1e503d.png)](https://p1.ssl.qhimg.com/t011ebb6ebc6f1e503d.png)

相反，如果获取环境变量失败，则会调⽤SetEnvironmentVariableW设置新的环境变量，这⾥很明显是在<br>
做环检测，如果样本第⼀次运⾏，系统中是肯定不会存在环境变量N92KG7KSpA21lGd2OPZA7QwZv，<br>
那么程序就通过SetEnvironmentVariableW设置环境变量N92KG7KSpA21lGd2OPZA7QwZv，然后在下<br>
⾯通过CreateProcess重新启动⾃身。

[![](https://p5.ssl.qhimg.com/t015cd62a4b5a5339a5.png)](https://p5.ssl.qhimg.com/t015cd62a4b5a5339a5.png)

重启之后结束掉当前进程：

[![](https://p1.ssl.qhimg.com/t018a1d4ca47e7cc22c.png)](https://p1.ssl.qhimg.com/t018a1d4ca47e7cc22c.png)

这⾥初步的执⾏流程搞清楚了，于是回到IDA中分析sub_10001270函数。

为了能够绕过这个检测正常调试，可以使⽤调试器附加regsvr32.exe

[![](https://p3.ssl.qhimg.com/t01b32e4ed6737589ae.png)](https://p3.ssl.qhimg.com/t01b32e4ed6737589ae.png)

附加之后，通过调试选项中的改变命令⾏，设置新的参数，新参数为dll的完整路径。

[![](https://p2.ssl.qhimg.com/t0187c2f76703f2cc7d.png)](https://p2.ssl.qhimg.com/t0187c2f76703f2cc7d.png)

添加参数之后，给GetEnvironmentVariableW设置断点，然后F9即可跑到需要调试的dll中。

[![](https://p0.ssl.qhimg.com/t0184b4397f147352c7.png)](https://p0.ssl.qhimg.com/t0184b4397f147352c7.png)

F8往下⾛，当程序执⾏完SetEnvironmentVariableW成功设置⽬标环境变量，⼜在dllinstall起始地址处重<br>
新设置eip，然后运⾏过来，此时GetEnvironmentVariableW将能够正常获取，能够跳转到下⾯的call<br>
sub_10001270。

进来之后，成功VirtualAlloc分配了00830000开始的⼀⽚内存

[![](https://p4.ssl.qhimg.com/t01d4f53cbeb3b7badb.png)](https://p4.ssl.qhimg.com/t01d4f53cbeb3b7badb.png)

### <a class="reference-link" name="%E8%AF%BB%E5%8F%96%E8%B5%84%E6%BA%90%E8%A7%A3%E5%AF%86shellcode"></a>读取资源解密shellcode

然后在12b处通过_memmove设置内存，将资源读取过来，这⾥读取的是名为1446资源的数据

[![](https://p3.ssl.qhimg.com/t011a97ac3d070a3d2f.png)](https://p3.ssl.qhimg.com/t011a97ac3d070a3d2f.png)

### <a class="reference-link" name="%E6%89%93%E5%BC%80%E8%AF%B1%E9%A5%B5%E2%BD%82%E4%BB%B6%E8%BF%B7%E6%83%91%E2%BD%A4%E6%88%B7"></a>打开诱饵⽂件迷惑⽤户

回到IDA中，进⼊下⼀个call sub_10001120中查看代码：

在sub_10001120中，⾸先会通过GetTempPathW获取%temp%路径

[![](https://p3.ssl.qhimg.com/t012ac9c9ce70e5653e.png)](https://p3.ssl.qhimg.com/t012ac9c9ce70e5653e.png)

接着创建并写⼊⼀个⽂件，通过ShellExecute打开

[![](https://p5.ssl.qhimg.com/t010434ca15fa6846bf.png)](https://p5.ssl.qhimg.com/t010434ca15fa6846bf.png)

创建的⽂件就是后续⽤于显示迷惑⽤户的docx⽂档

[![](https://p4.ssl.qhimg.com/t01b17b935653c74a6e.png)](https://p4.ssl.qhimg.com/t01b17b935653c74a6e.png)

可以在WriteFile函数出看到具体写⼊内容为docx⽂档：

[![](https://p2.ssl.qhimg.com/t01611f8cc7a20c30b8.png)](https://p2.ssl.qhimg.com/t01611f8cc7a20c30b8.png)

打开该⽂档以迷惑⽤户：

[![](https://p3.ssl.qhimg.com/t0101976582713ed15c.png)](https://p3.ssl.qhimg.com/t0101976582713ed15c.png)

通过这种模糊⽂档迷惑⽤户，是海莲花的常⻅攻击⼿法：

[![](https://p2.ssl.qhimg.com/t010608d3e07ce0b3e0.png)](https://p2.ssl.qhimg.com/t010608d3e07ce0b3e0.png)

⽂档打开之后，返回回去释放内存，然后执⾏ret ，sub_10001270函数执⾏完毕

[![](https://p3.ssl.qhimg.com/t01e2f8c9493b77e04d.png)](https://p3.ssl.qhimg.com/t01e2f8c9493b77e04d.png)

### <a class="reference-link" name="%E8%B7%B3%E8%BD%AC%E5%88%B0shellcode%E6%89%A7%E2%BE%8F"></a>跳转到shellcode执⾏

然后call eax，跳到先前分配填充的内存执⾏：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01b0ab4f905464f44b.png)

过来的代码就带了混淆了，记得设置快照继续往下调试。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t019b001a697dfc4d37.png)

往下⾛，会解密出⼀个域名放⼊eax中，然后作为参数call 830168 完整的域名是：jcdn.jsoid.com 这⾥可<br>
以跟进到这个call中，其实可以看到这个call的地址就在下⾯⼏⾏。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t016f7649626b134568.png)

call进来之后，程序会有很多解密指令和花指令，在解密过程中，有⼀些⼩地⽅需要注意，⽐如这⾥的jne<br>
是跳转到了jmp后⾯的⼀⾏语句，所以如果要设置断点或是通过F4跑完循环，请设置在jmp语句之后。

[![](https://p2.ssl.qhimg.com/t01115a25e9862c99de.png)](https://p2.ssl.qhimg.com/t01115a25e9862c99de.png)

### <a class="reference-link" name="%E5%B0%9D%E8%AF%95%E4%B8%8B%E8%BD%BDcobaltstrike%20%E5%90%8E%E2%BB%94"></a>尝试下载cobaltstrike 后⻔

跳过这些混淆之后，接下来程序会收集计算机的ComputerName、username和OS准备请求之前的地址下<br>
载后续payload，由于笔者捕获该样本的时候，域名已经被海莲花关闭，无法根据这个样本下载到后续payload继续分析。但根据之前的经验，这⾥下载的应该是Cobalt StrikeBeacon 后⻔。

[![](https://p0.ssl.qhimg.com/t015b840d52ec2b454b.png)](https://p0.ssl.qhimg.com/t015b840d52ec2b454b.png)

请求⽅式为GET，请求的参数为:eax:L”/script/word.png?A=WINGTVTJQVSKE4&amp;B=Administrator&amp;C=Windows_NT”

[![](https://p0.ssl.qhimg.com/t0158dcbb294f15e9ea.png)](https://p0.ssl.qhimg.com/t0158dcbb294f15e9ea.png)

请求完成之后，⽆论是否成功下载都结束函数，跳转到另外⼀⽚内存中继续执⾏。

依旧是⼤⽚混淆，通过多次跳转，不断的加载dll和所需的API<br>
通过call esi 获取⼀些API的地址，⽐如CreateStreamOnHGlobal

[![](https://p1.ssl.qhimg.com/t016eee5cc74883bdd2.png)](https://p1.ssl.qhimg.com/t016eee5cc74883bdd2.png)

通过LoadLibrary加载⼀些dll

[![](https://p1.ssl.qhimg.com/t01d7492e37de5dd82f.png)](https://p1.ssl.qhimg.com/t01d7492e37de5dd82f.png)

### <a class="reference-link" name="%E8%A7%A3%E5%AF%86%E7%89%B9%E2%BB%A2Denis"></a>解密特⻢Denis

然后进⾏VirtualAlloc分配内存空间

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t011c60666c756f1b4b.png)

填充PE头

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01446b8175bdbc79bd.png)

再⼀次分配内存：

[![](https://p1.ssl.qhimg.com/t01e6dd95282723cff2.png)](https://p1.ssl.qhimg.com/t01e6dd95282723cff2.png)

数据填充：

[![](https://p2.ssl.qhimg.com/t018971a8f19e01b35e.png)](https://p2.ssl.qhimg.com/t018971a8f19e01b35e.png)

多次分配内存之后call到02开头的内存中执⾏，⾥⾯是海莲花特⻢Denis

证据1：

[![](https://p3.ssl.qhimg.com/t01a38778e80a811d1a.png)](https://p3.ssl.qhimg.com/t01a38778e80a811d1a.png)

证据2：

[![](https://p2.ssl.qhimg.com/t01a931caa5f6ea3719.png)](https://p2.ssl.qhimg.com/t01a931caa5f6ea3719.png)

可以看到，上⾯程序已经尝试下载cs后⻔到本地执⾏，⽽在这⾥⼜解密了Denis，这是海莲花的双重载荷攻<br>
击。

过来之后，程序通过VritualAlloc在10000000分配了⼀⽚内存

[![](https://p2.ssl.qhimg.com/t0167840ee2f2579f41.png)](https://p2.ssl.qhimg.com/t0167840ee2f2579f41.png)

然后不断的开辟后⾯的内存空间，写⼊数据

[![](https://p2.ssl.qhimg.com/t01f1fcd0e2a646c3c0.png)](https://p2.ssl.qhimg.com/t01f1fcd0e2a646c3c0.png)

填充函数为2CBDD0

[![](https://p4.ssl.qhimg.com/t01f4a6e9b577248c65.png)](https://p4.ssl.qhimg.com/t01f4a6e9b577248c65.png)

直到填充完10058000这⽚内存

[![](https://p4.ssl.qhimg.com/t01c28685ae6ddc7988.png)](https://p4.ssl.qhimg.com/t01c28685ae6ddc7988.png)

然后通过call eax的⽅式call到新的PE中

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01c2f97fad2dd11423.png)

继续请求服务器，等待服务器响应之后执行后续的操作。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01e0c256656c1bcdc8.png)

程序会⼀直尝试循环请求三个地址：

jcdn.jsoid[.]com<br>
news.shangrilaexports[.]com<br>
clip.shangweidesign[.]com



## 0x06 总结

本次简单对海莲花的样本进⾏了分析，可以发现，该家族在19年年底使⽤的攻击⼿法和武器库，还是和19<br>
年上半年、18年时的差不多。同时也使用了一些比较新颖的攻击手法，比如下载cs后⻔和解密Denis的双重<br>
载荷攻击。这类攻击⼿法在2020年的海莲花样本中也还在沿⽤。由于Denis混淆比较严重，之前完整的分析过一次，本次分析的时候还是一不注意就被绕进去了。目前针对Denis的分析，我个人没有总结出比较高效的分析方法，都是直接调试器硬刚。之后如果总结出了比较好的方案再分享给大家~

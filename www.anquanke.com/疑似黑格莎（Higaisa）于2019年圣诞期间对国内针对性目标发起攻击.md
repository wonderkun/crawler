
# 疑似黑格莎（Higaisa）于2019年圣诞期间对国内针对性目标发起攻击


                                阅读量   
                                **645417**
                            
                        |
                        
                                                                                    





[![](./img/200467/t0135b9f72c46b10bba.jpg)](./img/200467/t0135b9f72c46b10bba.jpg)



## 背景

安恒信息安全研究院猎影实验室捕获到一个以圣诞为主题的样本，根据文档时间和释放载荷的编译时间，以及诱饵文档的内容，猜测真实攻击时间在2019年圣诞期间。根据一定关联发现该次攻击可能和黑格莎（Higaisa）组织有关。



## 分析

诱饵文档以圣诞为主题，内容为圣诞祝福：

[![](./img/200467/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/dm/1024_615_/t01b26bd41772a8d044.jpg)

该样本利用CVE-2018-0798漏洞进行攻击，打开文档后会在temp目录释放8.t文件，8.t为一个加密的文件，Encoder为“B0747746”，进行解密并会在Word启动目录创建“intel.wll”文件：

[![](./img/200467/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/dm/1024_395_/t010ed778db11cd0e8e.jpg)

当再次打开Word应用时会调用该wll程序，intel.wll程序会在%ALLUSERSPROFILE%目录下新建“TotalSecurity”文件夹，在该文件夹下释放360ShellPro.exe程序：

[![](./img/200467/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/dm/1024_324_/t019fc1d58b7a3a1e15.jpg)

并在utils目录下释放FileSmasher.exe程序：

[![](./img/200467/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/dm/1024_375_/t01fdf6f61b2a4695be.jpg)

还会创建自启动，在自启动目录添加LNK文件：

[![](./img/200467/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/dm/1024_255_/t01226f80c91b77a61b.jpg)

链接到360ShellPro.exe，包含启动参数“/func=5”：

[![](./img/200467/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/dm/802_1024_/t01ec74417b0286a2aa.jpg)

360ShellPro.exe是360一个早期版本程序的修改文件，将该文件和原始版本程序进行比较，发现只进行了一处修改：

[![](./img/200467/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/dm/1024_392_/t0165d452892f714059.jpg)

经修改后执行：

[![](./img/200467/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/dm/1024_282_/t01b20f2cefc644214d.jpg)

会执行到进程创建，将utils目录下的FileSmasher.exe程序运行起来：

[![](./img/200467/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/dm/1024_423_/t01a049b1b514e9f6e8.jpg)

而如果按照原先的代码执行：

[![](./img/200467/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/dm/1024_300_/t01cb43ced4e5acc2fa.jpg)

则会进行校验报出错误：

[![](./img/200467/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/dm/1024_235_/t018489ddf6ac6953d5.jpg)

攻击者修改原始程序使恶意文件FileSmasher.exe可以被正常调用执行。

FileSmasher.exe程序是一个Downloader程序，会下载下一阶段载荷进行后续攻击。

该样本和当前已披露的黑格莎Downloader程序功能基本相同，只有一些小的变化。

如和已披露样本Duser.dll（MD5：5de5917dcadb2ecacd7ffd69ea27f986）进行比较，

[![](./img/200467/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/dm/1024_501_/t01dbbdbe9af48fdb12.jpg)

可以看出功能大体上是一致的。

并且连接域名walker.shopbopstar[.]top也和黑格莎关联。

所以有一定理由怀疑这次攻击可能为黑格莎所为。

再来看一下这次攻击的攻击链路，

[![](./img/200467/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/dm/1024_297_/t01e2b42195a11ff50b.jpg)

攻击链的前半阶段，使用CVE-2018-0798释放wll文件，这类形式在多个组织都出现过，容易造成干扰，在已披露的黑格莎的攻击样本中也比较少见，但也有案例。并且更加引起注意的是该样本和某些组织使用的有更进一步的共同点，如8.t的Encode码相同，8.t的源路径相同，释放的temp路径相同，shellcode相同，但是最终的载荷不同。

[![](./img/200467/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/dm/1024_334_/t015b4a9a2bc9444bc3.jpg)

那么这存在一些可能：

1）这些组织间存在一定的联系；

2）这些组织购置了同类型的武器；

3）一些组织在获得了一些样本对其分析后自己写了个生成工具

或者其它更多可能。仍需要进一步分析。

后半阶段使用白加黑的手法并下载后一阶段载荷，黑格莎存在这样的手法。

关于“黑格莎”源于友商从攻击组织喜欢使用的RC4密钥“Higaisakora”来进行定义。将“Higaisakora”进行拆分，可以形成“Higa is a kora”，看上去似乎有一定的合理性，Higa可能是一个名字，使用地方比较广泛，如冲绳地区的姓：

[![](./img/200467/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/dm/1024_155_/t01e05ee3bf3ce8a322.jpg)

Kora则联想到某国。



## 小结

通过一定分析，可以有一定的理由怀疑次圣诞攻击活动可能和黑格莎（Higaisa）组织相关。



## IOC

Hash:

2123bf482c9c80cb1896ff9288ad7d60

59a55c7bbc0ee488ec9e2cf50b792a56

d5e42cc18906f09d5bab62df45b5fcf6

d5e42cc18906f09d5bab62df45b5fcf6

Domain:

walker.shopbopstar[.]top

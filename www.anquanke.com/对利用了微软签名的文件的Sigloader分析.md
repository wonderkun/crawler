> 原文链接: https://www.anquanke.com//post/id/242574 


# 对利用了微软签名的文件的Sigloader分析


                                阅读量   
                                **82592**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t0134e4cb9574e9ebb7.png)](https://p1.ssl.qhimg.com/t0134e4cb9574e9ebb7.png)



## 1.前期提要

在日常看威胁情报中发现一种利用Microsoft数字签名DLL文件的恶意软件，并且查询了披露出来的ioc信息发现没有杀软报毒，遂进行了分析。报告链接（[https://www.lac.co.jp/lacwatch/report/20210521_002618.html）](https://www.lac.co.jp/lacwatch/report/20210521_002618.html%EF%BC%89)

[![](https://p3.ssl.qhimg.com/t01224e7c4baef4e394.png)](https://p3.ssl.qhimg.com/t01224e7c4baef4e394.png)

[![](https://p4.ssl.qhimg.com/t01cb1e1cc20a947263.png)](https://p4.ssl.qhimg.com/t01cb1e1cc20a947263.png)

[![](https://p0.ssl.qhimg.com/t018819808063e47231.png)](https://p0.ssl.qhimg.com/t018819808063e47231.png)



## 2.样本概要

我从中选取了1个loader（1E750c5cf5c68443b17c15f4aac4d794）跟1个滥用微软签名的有效载荷文件（2F2E724DD7D726D34B3F2CFAD92E6F9A）

Loader就是一个没有签名的dll

[![](https://p4.ssl.qhimg.com/t0109812cb2493233d0.png)](https://p4.ssl.qhimg.com/t0109812cb2493233d0.png)

查看带有载荷的文件，发现确实有微软签名，但是文件有做过修改原始文件应该是UXLibRes.dll

[![](https://p5.ssl.qhimg.com/t01732db564e49d7fd3.png)](https://p5.ssl.qhimg.com/t01732db564e49d7fd3.png)

[![](https://p2.ssl.qhimg.com/t01bcf3a89ad103bf57.png)](https://p2.ssl.qhimg.com/t01bcf3a89ad103bf57.png)



## 3.样本分析

Loader的主要的功能实现就是sub_180001858函数，跟进这个函数

[![](https://p5.ssl.qhimg.com/t01716c191224514a75.png)](https://p5.ssl.qhimg.com/t01716c191224514a75.png)

sub_180001858函数首先获取当前进程的默认堆的句柄，然后从堆中分配一块分配0x58字节的内存并初始化为0，然后调用了一个解密函数传入加密函数的地址以及函数名称的长度作为参数进行解密，解密出的函数如下

[![](https://p5.ssl.qhimg.com/t017d6528f3b1bef9ab.png)](https://p5.ssl.qhimg.com/t017d6528f3b1bef9ab.png)

[![](https://p2.ssl.qhimg.com/t016397de0233f1dc0f.png)](https://p2.ssl.qhimg.com/t016397de0233f1dc0f.png)

解密函数主要就是传入了秘钥随机数以及加密数据，加密数据长度进行计算

[![](https://p4.ssl.qhimg.com/t012f2b71d84e09177f.png)](https://p4.ssl.qhimg.com/t012f2b71d84e09177f.png)

[![](https://p5.ssl.qhimg.com/t0178f14ff87069c855.png)](https://p5.ssl.qhimg.com/t0178f14ff87069c855.png)

进行了循环判断堆指针指向的值是否为空

[![](https://p4.ssl.qhimg.com/t01ecdcbeb69aa2a073.png)](https://p4.ssl.qhimg.com/t01ecdcbeb69aa2a073.png)

进入sub_180001000函数首先就有个if判断里面有2个判断条件，第一个是判断datalen-1的值是否小于等于0xEA,datalen-1值为0x4d第一个成立第二个是利用了RtlcomputerCrc32函数对datalen+4地址的数据块进行crc32计算，算出来的值与dword_1800168EC保存的数据进行比较验证数据块是否正常。Crc计算出来的值包括数据长度这些已经硬编码在数据块中

[![](https://p3.ssl.qhimg.com/t01124663c6ac73542a.png)](https://p3.ssl.qhimg.com/t01124663c6ac73542a.png)

[![](https://p1.ssl.qhimg.com/t01839b60fe78249095.png)](https://p1.ssl.qhimg.com/t01839b60fe78249095.png)

还是调用相同的解密函数传入秘钥随机值加密数据加密数据的长度进行解密

[![](https://p5.ssl.qhimg.com/t0189d152f130743742.png)](https://p5.ssl.qhimg.com/t0189d152f130743742.png)

[![](https://p5.ssl.qhimg.com/t0101db0367cbdd6acf.png)](https://p5.ssl.qhimg.com/t0101db0367cbdd6acf.png)

datalen解密前的数据

[![](https://p2.ssl.qhimg.com/t019e46825a6acfb9fa.png)](https://p2.ssl.qhimg.com/t019e46825a6acfb9fa.png)

datalen解密后的数据可以看到KBDTAM131.DLL字符串已经出来了

[![](https://p4.ssl.qhimg.com/t01eb2022413e497aca.png)](https://p4.ssl.qhimg.com/t01eb2022413e497aca.png)

分配新的堆空间heapPointer_1

[![](https://p5.ssl.qhimg.com/t016b9919dab7b2c252.png)](https://p5.ssl.qhimg.com/t016b9919dab7b2c252.png)

判断datalen数据块的长度满足就进行数据拷贝，拷贝了24个字节到新分配的堆空间

[![](https://p1.ssl.qhimg.com/t01e6c916dc4353513e.png)](https://p1.ssl.qhimg.com/t01e6c916dc4353513e.png)

[![](https://p2.ssl.qhimg.com/t0113aa7c5fbfa61ab0.png)](https://p2.ssl.qhimg.com/t0113aa7c5fbfa61ab0.png)

新分配了一块堆空间heapPointer_2用来存放KBOTAM131.DLL字符串

[![](https://p3.ssl.qhimg.com/t0139245faae7be00fa.png)](https://p3.ssl.qhimg.com/t0139245faae7be00fa.png)

[![](https://p2.ssl.qhimg.com/t0106c2425aae8aa6f9.png)](https://p2.ssl.qhimg.com/t0106c2425aae8aa6f9.png)

将KBOTAM131.DLL后面的所有数据拷贝到堆空间heapPointer_1中

[![](https://p0.ssl.qhimg.com/t01fc948239fff3f2a1.png)](https://p0.ssl.qhimg.com/t01fc948239fff3f2a1.png)

[![](https://p5.ssl.qhimg.com/t01dc96e71325c08732.png)](https://p5.ssl.qhimg.com/t01dc96e71325c08732.png)<br>
sub_180001000函数主要就是解密了datalen数据块然后将数据块的值拷贝新的2个堆空间中<br>
解密后的datalen数据块

[![](https://p3.ssl.qhimg.com/t015b539243be4a93f1.png)](https://p3.ssl.qhimg.com/t015b539243be4a93f1.png)

堆1原始数据

[![](https://p1.ssl.qhimg.com/t01e82eb59ab3a3a3ae.png)](https://p1.ssl.qhimg.com/t01e82eb59ab3a3a3ae.png)

拷贝后堆1数据

[![](https://p3.ssl.qhimg.com/t01b50588065f86020b.png)](https://p3.ssl.qhimg.com/t01b50588065f86020b.png)

堆2原始数据

[![](https://p2.ssl.qhimg.com/t01e4a7e98185a5821f.png)](https://p2.ssl.qhimg.com/t01e4a7e98185a5821f.png)

拷贝后的堆2数据

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t012f196711aab0f475.png)

sub_180001000函数执行返回后就是对新开辟的堆1偏移16的空间的值判断是否数据已经解密并且修改，然后获取了新EtwEventWrite函数的地址然后通过VirtualProtect修改内存属性修改了函数的前4个字节。

[![](https://p4.ssl.qhimg.com/t014f17f1fc6088e08c.png)](https://p4.ssl.qhimg.com/t014f17f1fc6088e08c.png)

[![](https://p2.ssl.qhimg.com/t01dd446692928fc8e4.png)](https://p2.ssl.qhimg.com/t01dd446692928fc8e4.png)

[![](https://p3.ssl.qhimg.com/t01bb2a471efde7b603.png)](https://p3.ssl.qhimg.com/t01bb2a471efde7b603.png)

然后继续根据堆1偏移4的值来判断用户名是否是system，这里由于值为0该判断条件里面的内容并未执行

[![](https://p1.ssl.qhimg.com/t01fa9c242915a9d70e.png)](https://p1.ssl.qhimg.com/t01fa9c242915a9d70e.png)

然后又对堆1偏移8的值进行了判断条件是或由于第一个条件值为0直接执行了下面的函数并未调用CreateMutex函数，CreateMutex函数跟进去如下图所示

[![](https://p2.ssl.qhimg.com/t01f9b21971fb621e3a.png)](https://p2.ssl.qhimg.com/t01f9b21971fb621e3a.png)

[![](https://p3.ssl.qhimg.com/t018e7e657d90297b8c.png)](https://p3.ssl.qhimg.com/t018e7e657d90297b8c.png)

下面就是主要的loader的执行方式了，通过DecodeData读取并解密含有载荷的有微软签名的dll然后申请内存空间创建线程执行

[![](https://p0.ssl.qhimg.com/t01c46dfc951619183a.png)](https://p0.ssl.qhimg.com/t01c46dfc951619183a.png)

跟进DecodeData函数里面一开始是判断堆1偏移20的空间的值是否为0，这里是为0的没执行获取当前模块名字的函数，然后执行else传递堆1偏移24空间地址里面的值，该值正好是堆2空间的指针，从堆2中获取KBDTAM131.DLL并设置为当前环境变量然后通过获取当前模块名称，并通过一系列路径的操作函数来拼接出KBDTAM131.DLL的绝对路径

[![](https://p1.ssl.qhimg.com/t01ee9d3a6454759528.png)](https://p1.ssl.qhimg.com/t01ee9d3a6454759528.png)

[![](https://p1.ssl.qhimg.com/t0159a171132b5cc4b5.png)](https://p1.ssl.qhimg.com/t0159a171132b5cc4b5.png)

[![](https://p2.ssl.qhimg.com/t01e76af8c9a6ebf448.png)](https://p2.ssl.qhimg.com/t01e76af8c9a6ebf448.png)

[![](https://p4.ssl.qhimg.com/t019d7a28e4e5841d55.png)](https://p4.ssl.qhimg.com/t019d7a28e4e5841d55.png)

这里主要就是打开带微软签名的文件然后读取里面文件偏移为0x2E10的地方读取0x3F00字节的数据，读取出来后存到新的堆空间堆3中.这里又可以发现最开始解密出来的堆1空间里面的偏移32代表了读取载荷的大小也就是0x3fa00,偏移36代表了载荷的偏移位置. 2个地址的数据相加来判断恶意签名文件大小

[![](https://p1.ssl.qhimg.com/t0186eb6693faf74dc1.png)](https://p1.ssl.qhimg.com/t0186eb6693faf74dc1.png)

[![](https://p3.ssl.qhimg.com/t01bf097526913b7dff.png)](https://p3.ssl.qhimg.com/t01bf097526913b7dff.png)

继续使用之前的解密算法传入了密钥，,堆1偏移44的地址，微软签名文件中读取的加密载荷,载荷的长度进行运算

[![](https://p3.ssl.qhimg.com/t0180fb68a0162eea76.png)](https://p3.ssl.qhimg.com/t0180fb68a0162eea76.png)

[![](https://p4.ssl.qhimg.com/t01a95bc900adba8d58.png)](https://p4.ssl.qhimg.com/t01a95bc900adba8d58.png)

[![](https://p5.ssl.qhimg.com/t0184e19f922dc4416d.png)](https://p5.ssl.qhimg.com/t0184e19f922dc4416d.png)

然后又使用RtlcomputerCrc32对解密出来的数据进行计算然后与硬编码在堆1空间偏移40地址的值进行比较，我这里是校验不通过的可能是loader跟载荷文件不对应导致的可以修改zf标志位来绕过校验返回1就可以了

[![](https://p5.ssl.qhimg.com/t0163d761e079f12956.png)](https://p5.ssl.qhimg.com/t0163d761e079f12956.png)

[![](https://p2.ssl.qhimg.com/t01c43045da0c654ce3.png)](https://p2.ssl.qhimg.com/t01c43045da0c654ce3.png)

[![](https://p2.ssl.qhimg.com/t01a2b1a1dd30e8e9d5.png)](https://p2.ssl.qhimg.com/t01a2b1a1dd30e8e9d5.png)

解密后的文件简单看了下是CS的beacon反射加载dll,ioc与报告中一致

[![](https://p2.ssl.qhimg.com/t0137a13118546a808d.png)](https://p2.ssl.qhimg.com/t0137a13118546a808d.png)

[![](https://p3.ssl.qhimg.com/t0175c099e82bdf4677.png)](https://p3.ssl.qhimg.com/t0175c099e82bdf4677.png)

[![](https://p5.ssl.qhimg.com/t018229b5819170ec5c.png)](https://p5.ssl.qhimg.com/t018229b5819170ec5c.png)<br>
主线程后续会判断堆1偏移12里面的值来进行自删除的操作删除最外层的loader

[![](https://p0.ssl.qhimg.com/t01578d014feb1dd36d.png)](https://p0.ssl.qhimg.com/t01578d014feb1dd36d.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t010b594f08c789189f.png)



## 4.总结

该loader的加载方式并不复杂,读取带有微软签名的载荷文件解密创建线程执行，loader本身也是被各大厂商查杀，只是拥有白签名的载荷确实能躲避大部分杀软的查杀。

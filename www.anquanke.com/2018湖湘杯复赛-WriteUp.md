> 原文链接: https://www.anquanke.com//post/id/164604 


# 2018湖湘杯复赛-WriteUp


                                阅读量   
                                **390006**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">11</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/dm/1024_672_/t01fdfc5d7faea35bad.jpg)](https://p4.ssl.qhimg.com/dm/1024_672_/t01fdfc5d7faea35bad.jpg)

> By DWN战队

web这块基本都是原题，仅作参考。

差一题pwn200 AK。

## 签到题 SingIn Welcome

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://raw.githubusercontent.com/evilwing/wing-images/master/img/20181119002216.png)



## WEB Code Check

访问是一个登陆页面，查看源码有一个链接。

尝试注入，一直返回数据库错误。

然后在news目录下发现源码list.zip

b3FCRU5iOU9IemZYc1JQSkY0WG5JZz09就是1加密过的。

需要逆推一下这个函数。

然后将我们的payload直接加密然后注入。

由于比较麻烦，tamper省事一点

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://raw.githubusercontent.com/evilwing/wing-images/master/img/20181119000007.png)

hxb.py

很多人没注意notice2

直接一把嗦：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://raw.githubusercontent.com/evilwing/wing-images/master/img/20181119000157.png)



## WEB XmeO

没啥好说的，基本的SSTI

直接找xss bot源码

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://raw.githubusercontent.com/evilwing/wing-images/master/img/20181119000558.png)

hh

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://raw.githubusercontent.com/evilwing/wing-images/master/img/20181119000457.png)



## WEB MyNote

注册一个账号，发现可以上传。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://raw.githubusercontent.com/evilwing/wing-images/master/img/20181119000914.png)

查看上传的图片

有一个picture的cookie

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://raw.githubusercontent.com/evilwing/wing-images/master/img/20181119001224.png)

数组的反序列化读取文件。

robots.txt可以知道存在flag.php

payload：

发送过去，看到了data协议的数据。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://raw.githubusercontent.com/evilwing/wing-images/master/img/20181119001348.png)

解码

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://raw.githubusercontent.com/evilwing/wing-images/master/img/20181119001401.png)



## WEB ReadFIle

这题也没什么考点，emmm。

file协议可以读取到文件。

首先发现ssrf目录下的web.php

出题人原意可能是想让我们用gopher打。

但是源码里面有一个这个：/var/www/html/ssrf/readflag

curl 保存到本地。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://raw.githubusercontent.com/evilwing/wing-images/master/img/20181119001957.png)

用ida分析一下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://raw.githubusercontent.com/evilwing/wing-images/master/img/20181119002035.png)

flag在ssrf目录…..

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://raw.githubusercontent.com/evilwing/wing-images/master/img/20181119002057.png)

gopher参考：

> 这次的re难度不是太大……但是re2和re3都有点偏门，不太硬核233 但也挺有意思的



## Replace

upx -d脱壳，然后是一个比普通签到略复杂一点的签到题，没什么好说的

要求table[input[i]] == atoi(data[2*i]+data[2*i+1])^0x19



## HighwayHash64

从题目和描述的Hash，以及输入提示的

> Note:hxb2018`{`digits`}`

就可以猜到，这估计是个爆破Hash的题目

看了一下hash函数中初始化结构体的部分跟md5不同，查了也没有信息，所以可能是自定义的哈希算法

刚开始尝试了一下扒代码到编译器中复现，然而有很多ROL的宏定义，比较麻烦，所以直接调用该函数是比较方便的

调用函数有两种方法，一种是写一个dll注入到exe中进行调用，另一种则是将该exe直接改成dll，另外写一个exe来调用

前者日后再尝试吧，相对而言感觉要复杂一些

后者只需要将exe的PE头中的标志位修改，再通过RVA(Relative Virtual Address)获取函数地址即可

具体方法为，首先通过十六进制编辑器修改PE头

这里使用010Editor一类的工具会比较方便
<li>NtHeader
<ul>
<li>Characteristics
<ul>
- IMAGE_FILE_DLL标志位
将该位改为1即可通过LoadLibrary调用

注意编译的时候由于dll是x64的，因此exe理应也是用x64的

以及这里的函数声明需要使用__fastcall的调用约定，因为从汇编可以看出来

传参使用的rcx和rdx，如果用其他调用约定的话通常会用栈传参

IDA其实是已经识别出来的

返回值则需要自己根据内容看出来，向rax放了一个int64的值

这里IDA是识别错误的

接下来就可以直接使用该函数来爆破了

第一次hash使用的是len的地址，也就是把长度视作一个4字节的char数组来进行hash

因此我们首先要算出flag的长度

爆破的时候也提供一个int的空间即可

很快可以得出i=19，然后掐去前后的格式字符共9个，即可知道中间的内容是十个十进制数了

接下来可以通过sprintf快速制作10个字节的十进制数，然后穷举

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://i.imgur.com/pdC2p5P.png)

赛后交流了一下，flag的hash是不一样，所以复现的时候需要自己改一下



## More efficient than JS

题目文件下载下来就能看到一个wasm，再结合题目，很显然又是WebAssembly逆向……越来越多的出题人开始搞这东西了orz

目前Chrome和Firefox都没有针对它出好用的调试器，只能用js的调试器凑活看，所以我的经验就是直接动调，用wabt组件反编译出的c和wat来辅助分析

运行了一下直接在fetch的地方报错，让队里师傅给搭了个http环境才能跑起来

以往的wasm题目都是在html中调用函数，这次找了一圈也没有看到

跑起来以后什么都不显示直接弹窗，估计是js中的代码，于是根据提示内容”Input:”找到了这里

[![](https://i.imgur.com/wkrsFl3.png)](https://i.imgur.com/wkrsFl3.png)

在这下断，然后刷新果然断到了，但是接着单步跟下去就会进到一个死循环里

[![](https://i.imgur.com/9dGo3Pi.png)](https://i.imgur.com/9dGo3Pi.png)

这个循环执行完以后又会回到弹窗里，于是有点懵逼

（动态调试和静态分析的相关技巧可以在我前两天的[博客](https://blog.csdn.net/whklhhhh/article/details/84146188)中找到）

后来在wat里发现了一个函数的名字叫做_main

果断下断，发现刷新页面以后会先执行wasm中的_main函数，然后到f98的调用时开始弹窗，点击取消以后会继续执行

再往后两个调用，到f42的时候注意它的参数执行完后会取出值，返回值则是len

然后在f22的5个参数中就可以发现各种有趣的东西了，注释如下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://i.imgur.com/48Wm0sb.png)

其中f22是核心的加密函数，在里面不断地单步跟，有选择地跳过

（其实最关键的就是几个循环中的i32_load），看它们从哪里取值以及取出来的是什么值即可

个人认为wasm的关键在于跟随数据而不是代码（因为代码太恶心了orz）

中间可以看到根据key去往后table中取值，但是最后与输入有关的只是异或，因此可以输入一串0，从而得到异或的值

然后从f23中的一个循环中使用的地址得到结果数组，最后异或求解即可

> flag`{`happy_rc4`}`

从这个flag来看算法应该是rc4，也比较负责动调中感觉到的，根据key变换table然后取table的值和明文异或

因为这个算法的特性所以也可以理解为和密钥流异或23333



## MISC Hidden Write

010看到3个ihdr和iend，分别抠出来，补齐png头89 50 4E 47 0D 0A 1A 0A

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://i.loli.net/2018/11/19/5bf194e3ea2fd.png)

后面的两个图片存在盲水印，解出来得到flag最后一段

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://i.loli.net/2018/11/19/5bf19542cc3d1.png)

文件结尾字符串得到flag中间一段

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://i.loli.net/2018/11/19/5bf1955dda475.png)

然后是一个lsb隐写找到flag的第一段

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://i.loli.net/2018/11/19/5bf1959a0f7de.png)



## MISC Flow

首先跑wifi密码，开始跑8位数字没跑出来，于是换了一个wpa常用密码的字典去跑，秒出结果orz

[![](https://i.loli.net/2018/11/19/5bf1971b2bf4e.png)](https://i.loli.net/2018/11/19/5bf1971b2bf4e.png)

参考：[https://xz.aliyun.com/t/1972](https://xz.aliyun.com/t/1972)

解密流量，然后跟踪tcp流，得到flag

[![](https://i.loli.net/2018/11/19/5bf196cb56058.png)](https://i.loli.net/2018/11/19/5bf196cb56058.png)



## MISC Disk

用winimage打开看到4个flag.txt

[![](https://i.loli.net/2018/11/19/5bf197441acb7.png)](https://i.loli.net/2018/11/19/5bf197441acb7.png)

提取后看到是一堆01串，脚本解一下

[![](https://i.loli.net/2018/11/19/5bf19758d1906.png)](https://i.loli.net/2018/11/19/5bf19758d1906.png)



## PWN Regex Format

保护全无，所以做法有很多了，我的思路是往bss上写shellcode，然后栈溢出劫持控制流到我布置好的shellcode上。

[![](https://i.loli.net/2018/11/19/5bf1978b1cdaf.png)](https://i.loli.net/2018/11/19/5bf1978b1cdaf.png)

这题比较烦的就是逆向部分了吧，首先读取regex format到.data的aBeforeUseItUnd变量后，这是做正则表达式的。然后读取一个字符串到bss上，是正则表达式匹配的对象。

程序首先会在0x08048680处的函数对正则表达式进行一个解析，比较烦的是，前面的内容是固定的Before :use$ it, :understand$* it :first$+.，即aBeforeUseItUnd变量

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://i.loli.net/2018/11/19/5bf198b4c139e.png)

一顿操作后将正则表达式分成了好几段，我们gdb看下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://i.loli.net/2018/11/19/5bf199179f49b.png)

然后这里进行循环去匹配每段正则表达式

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://i.loli.net/2018/11/19/5bf1995a55a4f.png)

不过sub_8048930的第3个参数为s，而s是char s; // [esp+474h] [ebp-D4h]，那这里就可以去进行一个栈溢出操作了，去这个函数看看

[![](https://i.loli.net/2018/11/19/5bf199cbcc876.png)](https://i.loli.net/2018/11/19/5bf199cbcc876.png)

可以看到，只要正则匹配，程序就会一直进行一个赋值操作，将bss上的数据赋值给栈上的s，于是问题就是如果使这个正则一直匹配下去。很简单，我们把bss上要写的内容放进去就行了嘛。

经过一顿调试后，最终写出了如下exp

[![](https://i.loli.net/2018/11/19/5bf19ad518bec.png)](https://i.loli.net/2018/11/19/5bf19ad518bec.png)

完整exp：



## PWN Hash Burger

[https://github.com/SECCON/SECCON2017_online_CTF/tree/0a8bbd28544fbd89bed0f0e3eafa7b09a0165a6b/pwn/300_hash_burger](https://github.com/SECCON/SECCON2017_online_CTF/tree/0a8bbd28544fbd89bed0f0e3eafa7b09a0165a6b/pwn/300_hash_burger)

Get原题一枚，exp拿下来，改下ip，端口，libc路径，直接打

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://i.loli.net/2018/11/19/5bf19b412f293.png)



## Crypto Common Crypto

很明显有两个函数与加密相关

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://i.imgur.com/8QDLCYq.png)

key_generate函数中对key_struct的前16个字节进行了赋值，也就是128位的key

然后在之后与一个数组—搜索之后可以发现它是AES的SBox，进行异或，产生了轮密钥

然后在下一个函数，AES_encrypt中进行了明文和key_struct的运算

AES的特征是十轮运算、每轮进行字节替换、行移位、列混淆、轮密钥加，最后一轮缺少轮密钥加

所以要不是在十轮循环中有一个判断，要不就是九轮循环+额外三个步骤

函数内是满足这样的流程的

使用AES进行加密与动调获得的结果可以互相验证

sprintf调用了32次，而加密的结果只有16个字节，因此结果字符串中前32个字符为密文，后32个字符为明文的hex_encode

前半段进行解密、后半段则hex_decode即可

Good Job！

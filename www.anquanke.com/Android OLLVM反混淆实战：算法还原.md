
# Android OLLVM反混淆实战：算法还原


                                阅读量   
                                **701955**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">28</a>
                                </b>
                                                                                                                                    ![](./img/201459/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](./img/201459/t01496d2eb266e235ee.jpg)](./img/201459/t01496d2eb266e235ee.jpg)



## 前言

之前一篇我们已经讨论了android arm平台下的ollvm平坦化混淆还原的基本方法，这一篇我们就接着上一篇，继续实战反混淆。

apk样本：douyin9.9.0<br>
so样本：libcms.so<br>
逆向工具：ida



## 跟进

[![](./img/201459/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015445236b36b8c4cd.png)

上一篇末尾我们对Jni_Onload的最外层进行了反混淆，f5之后可以看到，主要调用了sub_10710和sub_23B0两个函数，跟进sub_10710,并没有发现对vm的引用，而在sub_23B0中引用了vm，所以先分析sub_23B0。

[![](./img/201459/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t013df351b06dcb9ba6.jpg)

跟进后该函里面是一段简单的混淆数，最终其实是跳转到了sub_23C6处的函数。

sub_23C6中存在这上一篇遇到的常规混淆，利用脚本将其清除之后，可以分析出该函数的作用是跳转到调用sub_23B0的第一个参数的地址，同时将javaVM指针的地址作为第一个参数传入到sub_23C6,通过ida动态调试我们得出sub_23B0的第一个参数为0x2520，所以我们继续，跟进到sub_0x2520。

[![](./img/201459/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0186f60704a8b0f7f9.jpg)

观察该函数cfg和内部特征，可以得出该函数又是经过ollvm平坦化处理，利用之前的去混淆脚本配置好之后进行处理：

[![](./img/201459/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01350541eccc7320f0.jpg)

部分f5之后的c代码：

[![](./img/201459/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t019200eb638e522c60.jpg)

并没有直接找到后面引用到javaVM指针的代码，但是上图2处看结构很可能是调用vm-&gt;getEnv，为了进一步优化f5代码和变量之间关系，我们需要进一步处理。可以注意到其中一些分支其实是不会执行的，如上图中1处分支的条件，从数学角度分析该条件不会成立，但ida并不能识别出来，所以我们在符号执行的时候需要特殊处理，去掉这些不会执行的相关块。

第二次优化处理后：

[![](./img/201459/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t011f2d8d003745a05b.jpg)

[![](./img/201459/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01a4064101bb8a8fcf.jpg)

这次可以看到JavaVM指针被直接引用到，函数执行的流程也基本上一览无遗，该函数里主要对一些全局变量进行解密，解密成用于注册jni方法的字符串或是其他用途的重要数据。

[![](./img/201459/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01d34f6997820d8387.jpg)

我们找到env-&gt;RegisterNatives处，然后通过参数获取到leviathan方法的对应的native函数地址位于0x576dc处。

0x576dc同样是和之前一样，存在常规跳转混淆和平坦化混淆，反混淆脚本伺候之：

[![](./img/201459/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0120cf7c52af95b28d.jpg)

[![](./img/201459/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01fa582efaa80c9886.jpg)

最后又是调用了sub_23B0这个函数，在前面已经分析过该函数的作用，可以看出，并没有直接将env等一些jni参数直接传入该函数，而是构建了一个可能是数组的结构，将这些参数加上一定的偏移放入该结构，再将该数组地址作为第二个参数传入。<br>
第一个参数表达式其实是一个定值，其值是sub_551c0的地址，不会受到表达式中变量a4影响（大家有兴趣可以验证下）。

进入到sub_551c0，又是ollvm+跳转混淆，老样子，脚本跑一跑。<br>
f5之后：

[![](./img/201459/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t011709e3abb5230d51.jpg)

[![](./img/201459/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01ac7d155ee9c4aa25.jpg)

可以看到在上图处取出了jni方法的参数，紧接着，对java层传入的数组和参数i2进行了一些简单的字节变换操作，将变换后的的数组，数组大小以及i1的值作为一个新的结构传入到sub_215BC。从后面调用的jni函数来看，sub_215BC的返回值极可能是最终加密之后的byte数组，所以我们继续跟进去：

[![](./img/201459/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01411f8610626470ea.jpg)

这里我对参数结构进行了一些转换，以便于更好的理解c代码，可以发现参数结构体作为一个数组的成员继续传入到下一层，继续跟进到sub_229C8：

该函数就是加密算法的核心位置了，但乍一看混淆方式貌似和前面的方式不太一样，该函数是纯ARM指令，也就用不了之前的脚本，而且混淆方式也不太像是ollvm，仔细观察这个函数可以发现里面有大量的switch-case跳转表结构，但ida没有识别出来，我们可以自己设置添加跳转表结构：

[![](./img/201459/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01787f807a2ce8b301.jpg)

如上图r6是索引值，r1是跳转表基址，r3是跳转表索引到的值，最后跳转的位置即r1+r3。在ida依次选择Edit-&gt;Other-&gt;Specify switch idiom，为此处配置一个跳转表结构：

[![](./img/201459/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01e5029f816faaa902.jpg)

找到所有的跳转表后，便可以f5查看c代码：

[![](./img/201459/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t016a5a4469701a39f4.jpg)

[![](./img/201459/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01bddfa2023de01be0.jpg)

[![](./img/201459/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01f431b82da2fa17e0.jpg)

基本上无法解读，但大体上可以知道其结构，while循环内的switch-case结构，但多数case内又嵌套着另一层switch-case结构，形成多层嵌套，所以代码看起来比较复杂。而最外层switch的case索引，是通过读取从dword_85B60起始的一串数据表，再通过转换运算得到。该数据表内的数据相当于一条命令，不同的命令可以执行不同的case组合，完成不同的功能。



## 用C代码实现流程

还原该算法难度较大，主要是while内switch case循环次数很多，经验证，总共有一万多次循环，如果对每次循环都进行分析的话，工作量可想而知。所以这里可以另辟蹊径，可以试着新建一个c工程，将f5的伪代码复制出来，同时再构建一个与当前程序执行环境相同的内存环境，直接脱机运行：

```
FILE* fp = fopen("libcms-dump", "rb");
    if (!fp)return-1;
    fseek(fp, 0L, SEEK_END);
    int size = ftell(fp);
    //将dump下来的so放入到申请的内存里
    pBuf = new char[size] {0};
    fseek(fp, 0L, SEEK_SET);
    fread(pBuf, size, 1, fp);
    fclose(fp);
    //对so进行数据重定位修复，ori_addr是dump so时，so的加载基址
    relocation(pBuf, ori_addr);
    const char* data="b6a274acedea791afce92a344ccdd80d00000000000000000000000000000000063745505e61c692b79747ec710f8a3100000000000000000000000000000000";
    int ts = 1583457688;
    unsigned char* pBuf3 = (unsigned char*)malloc(64);
    HexStrTobytes((char*)data, pBuf3);
    int swapts = _byteswap_ulong(ts);
    char* pBuf2 = (char*)malloc(20);
    sub_112D8((uint8*)pBuf2, pBuf3, 4);
    sub_112D8((uint8*)pBuf2+4, pBuf3+16, 4);
    sub_112D8((uint8*)pBuf2+8, pBuf3+32, 4);
    sub_112D8((uint8*)pBuf2+12, pBuf3+48, 4);
    sub_112D8((uint8*)pBuf2+16, (unsigned char*)&amp;swapts, 4);
    sub_112D8((uint8*)pBuf2 + 12, (unsigned char*)pBuf+0x8f09c, 4);
    MYINPUT input2 = { pBuf2,20,-1 };
    unsigned int a2[354] = { 0 };
    a2[0] = (unsigned int)&amp;input2;
    a2[2] = (unsigned int)&amp;pBuf[0x21ef5];
    a2[3] = (unsigned int)&amp;a2[350];
    a2[352] = pBuf[0x90690];
    MYINPUT* pInput = &amp;input;
    sub_229C8((unsigned int*)&amp;pBuf[0x85b60], a2, (unsigned int*)&amp;pBuf[0x8eb70], (unsigned int*)&amp;pBuf[0x8eba0], &amp;a2[2]);
```

因为该代码内用到了很多的全局变量，很多变量都是在app运行后才开始解密，我们也没有对那些代码进行分析，所以需要将app运行到sub_229c8时的整个libcms.so的内存dump出来，可以通过xposed+cydia或是frida hook sub_229c8来实现dump，同时记录下其加载基址，因为android平台pic（位置无关代码）编译的原因，所有全局变量的引用都是通过got(全局偏移表)完成的，加载器会根据加载基址来修正，并向got填入正确的全局变量的地址。当我们自己实现该函数功能，申请一段内存pBuf来存放so数据，把got内全局变量的地址修正到pBuf的位置，如某重定位数据a=S，app运行时的基址是A，pBuf的地址是B，则重定位a的值为S-A+B，这样便相当于从pBuf处加载so。

通过readelf -D 获取数据重定位信息：

[![](./img/201459/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01cbdf979eba48de02.jpg)

对数据进行重定位：

```
void relocation(char* bytes,uint32 ori_addr)
{
    uint32 new_addr = (uint32)bytes;
    unsigned int reldyn_start = 0xbac + new_addr;
    size_t reldyn_size = 5496;
    Elf32_Rel* pRel = (Elf32_Rel*)reldyn_start;

    //relocation for .rel.dyn
    for (int i = 0; i &lt; reldyn_size / sizeof(Elf32_Rel); ++i) 
    {
        uint8 relType = (pRel-&gt;r_info)&amp;0xff;
        if (relType == R_ARM_RELATIVE || relType == R_ARM_GLOB_DAT)
        {
            *(uint32*)(bytes + pRel-&gt;r_offset) = *(uint32*)(bytes + pRel-&gt;r_offset) -ori_addr + new_addr;
        }
        pRel += 1;
    }
}
```

在sub_229c8内有多处函数调用，同样需要把这样函数复制出来实现，需要注意的时这个地方：

[![](./img/201459/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t015ce91b84f40b4e06.jpg)

1147行是一个函数调用，v102的值分析后得出是sub_21ef4地址，其功能也很简单：

[![](./img/201459/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t010815db71beef9570.jpg)

考虑到a1可能有多个不同值，所以通过hook sub_21ef4，来获取所有app运行用到的a1的值，之后找到所有a1指向的函数并复制出来实现：

[![](./img/201459/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014d251b1908a26f11.jpg)

这样我们直接运行代码：

[![](./img/201459/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0138fade30c3acfb92.jpg)

成功获取返回值，为了验证正确性，将我们程序得到的结果放入到请求参数中，可以正常返回数据！！！

当然小弟我也是最后也是用了些偷投机取巧的方式实现了算法脱机，有耐心或是牛逼的同学可以试着直接逆向出算法。。遇到问题大家可以交流一番。。



## 总结

对于这次逆向，总体上ollvm混淆强度不大，可以通过反混淆脚本还原算法流程，算法核心位置的混淆比较难还原，需要一定技术水平或耐心，后面有时间的话我也会试着完整还原，敬请关注哈！！

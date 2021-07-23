> 原文链接: https://www.anquanke.com//post/id/216282 


# 利用WinAFL对闭源软件进行漏洞挖掘


                                阅读量   
                                **133991**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                    



[![](https://p1.ssl.qhimg.com/t01811598a5a7992775.jpg)](https://p1.ssl.qhimg.com/t01811598a5a7992775.jpg)



作者：lawhack@维阵漏洞研究员**<br>**

## 摘要:

winafl是谷歌的projectzero团队成员的fuzz工具力作，继承于afl，利用多种方式（IntelPT、DynamoRIO）对windows平台的软件进行动态插桩，同时也可以使用Syzygy进行静态插桩（必须具有完备的pdb符号文件）。由于IntelPT需要有硬件支持，同时必须在特定的win10版本之上才能使用，因此我在这里使用更为通用的DynamoRIO进行动态插桩来配合winafl。



## 准备:

1、编译安装winafl、DynamoRIO

我选择利用vs2017的x86_x74兼容命令提示工具进行编译，使用的是10.0.17763.0版本的sdk，能够正常编译。

2、选择目标

针对图像处理软件，我选择了wps photo这款程序，目前是最新版（11.1.0.1210）。

3、部署

在win7 32位平台下进行测试，8核cpu，16G内存。



## 漏洞挖掘步骤：

### <a class="reference-link" name="%E4%B8%80%E3%80%81%E9%80%86%E5%90%91%E5%88%86%E6%9E%90%E7%A8%8B%E5%BA%8F%EF%BC%8C%E6%89%BE%E5%88%B0%E9%80%82%E5%90%88fuzz%E7%9A%84%E5%87%BD%E6%95%B0"></a>一、逆向分析程序，找到适合fuzz的函数

目前我想到的fuzz目标程序的方式大致有两种，一是直接fuzz目标主程序，找到合适的函数地址就可以进行持续性fuzz；第二种是找到主程序所使用的第三方库文件，如果存在第三方库文件，就可以编写独立程序加载该第三方库，并调用对应的导出函数即可。

这两种方式各有优劣，第一种方式会导致前期的准备工作量减少，但问题是当你找到的函数地址不太合适时，将会大大降低fuzz效率；第二种方式则需要做更多的前期准备工作，而且如果开发者并没有使用独立的第三方库，而是使用静态编译等方式将对应库的代码混杂在自身的程序中，则很可能无法找到对应的第三方库进行fuzz，但是如果找到的话，则会大大提升后期的fuzz效率。

我对wpsphoto+.exe程序进行逆向分析，利用x64dbg对主程序进行调试，由于wpsphoto+.exe程序支持命令行启动，所以我们可以将图片的名称作为参数传递给程序，wpsphoto+.exe会加载该图片并进行显示。

但是由于程序在解析图片前会做很多的初始化操作，其中包含了大量的读写文件操作，我对Openfile写了条件断点，但发现并没有断下来，所以直接调试打开后的wpsphoto+.exe，接着对文件类操作的api下断，主要是openfile以及readfile函数，打开一张图片后发现断在了Readfile函数上，而且当前所处的模块为photo.dll，我利用IDA对该dll进行分析，导入函数如下：

[![](https://p4.ssl.qhimg.com/t01f0102d1fd68e011f.png)](https://p4.ssl.qhimg.com/t01f0102d1fd68e011f.png)

可以看出我们没有使用常规的Openfile函数，而是使用了fopen、wfopen函数作为替代，这导致了函数无法中断。

接下来再次重启应用程序，在这两个函数下断，发现程序能够正常中断。查看调用堆栈如下：

[![](https://p2.ssl.qhimg.com/t014399925c369d5dc4.png)](https://p2.ssl.qhimg.com/t014399925c369d5dc4.png)

可以看出整个调用链相对复杂些。但是经过测试后我发现，通过命令行打开图片和通过GUI打开图片的调用栈不一样，相对来说使用命令行更简单些，主要是命令行版的会优先解析图片，然后再利用QT进行加载、显示，调用栈如下：

[![](https://p3.ssl.qhimg.com/t010b8513cc64941fca.png)](https://p3.ssl.qhimg.com/t010b8513cc64941fca.png)

在深入的分析后，我并没有发现可供利用的第三方库函数，这样暂时无法编写harness code来fuzz了，只能尽量找到合适的函数地址来进行主程序fuzz。

### <a class="reference-link" name="%E4%BA%8C%E3%80%81%E5%AF%B9%E5%87%BD%E6%95%B0%E5%81%8F%E7%A7%BB%E8%BF%9B%E8%A1%8Cdebug%E6%B5%8B%E8%AF%95"></a>二、对函数偏移进行debug测试

利用winafl的debug模式进行测试，命令如下：<br>`drrun.exe -verbose -c winafl.dll -debug -t 900000 -m none -coverage_module photoview.dll -target_module photoview.dll -target_offset xx -call_convention thiscall -nargs 2 -fuzz_iterations 10 -- wpsphoto+.exe xx.jpg`

我在这里简单的对命令做些说明。

1、利用drrun.exe加载winafl.dll时必须是debug模式，这样会在当前目录生成一个log文件，并且能够和winafl通过pipe管道建立正常的通信。

2、-t 选项代表着超时时间限制，如果程序解析单个文件的时间超过这个时间就会按照hang来处理。

3、-m 代表着内存限制，意味着程序所能利用的最大内存，一般设为none。-coverage_module 则是需要进行覆盖率监测的模块，这里可以选择一个也可以选择多个。

4、-target_module 是目标模块，同target_offset相配合，选择的函数地址偏移就是根据目标模块计算的，是进行持续性fuzz的关键。

我最初在利用winafl的debug模式进行测试的时候出现了些问题，因为目前看到的目标模块名字叫photo.dll，所以最开始进行测试的时候给的名字也是photo.dll，但是查看log文件发现并没有进行插桩，目标函数也没有到达，分析所有加载的模块名称，发现加载了photoview.dll，我怀疑这是同名文件，于是查看了文件属性：

[![](https://p1.ssl.qhimg.com/t0130924a2e06882824.png)](https://p1.ssl.qhimg.com/t0130924a2e06882824.png)

改成photo view.dll后发现可以插桩了，log如下：

[![](https://p5.ssl.qhimg.com/t01f8ada3b535cd9345.png)](https://p5.ssl.qhimg.com/t01f8ada3b535cd9345.png)

同时需要注意的是call_convention这个参数，这同样非常关键，因为当程序从选定的函数执行返回后，DynamoRIO会恢复整个程序的context到目标函数开始执行前，因此我们必须明确目标函数的调用约定，而winafl默认的调用约定是stdcall，错误的调用约定可能导致程序在后续的迭代fuzz过程中崩溃，log如下：

[![](https://p5.ssl.qhimg.com/t01c28df45599d43ff0.png)](https://p5.ssl.qhimg.com/t01c28df45599d43ff0.png)

经过不断调整后，正确的log输出如下：

[![](https://p4.ssl.qhimg.com/t01b5852c49a541e6a1.png)](https://p4.ssl.qhimg.com/t01b5852c49a541e6a1.png)

### <a class="reference-link" name="%E4%B8%89%E3%80%81%E7%B2%BE%E7%AE%80%E6%A0%B7%E6%9C%AC"></a>三、精简样本

winafl提供了winafl-cmin.py的python脚本用来精简样本，原理大致是利用afl-showmap程序来获取每个样本的覆盖率状况，将相同覆盖率的样本进行剔除。命令如下：<br>`python winafl-cmin.py -i E:\samples -o E:\sampleout -t 1000000 -D E:\fuzztools\dynbuild32\bin32\ -coverage_module photoview.dll -target_module photoview.dll -target_offset xx -nargs 2 -- wpsphoto+.exe @@`

这样将精简过后的样本保存到特定文件夹后，我们就可以进行fuzz了。

### <a class="reference-link" name="%E5%9B%9B%E3%80%81%E5%BC%80%E5%A7%8Bfuzz"></a>四、开始fuzz

确定该函数偏移可以利用后，利用afl-fuzz主程序进行fuzz，命令如下：<br>`afl-fuzz.exe -i in -o out -t 90000 -m none -D E:\fuzz_target\tools\fuzztools\dynbuild32\bin32\ -- -call_convention thiscall -coverage_module photoview.dll -target_module photoview.dll -target_offset xx -fuzz_iterations 50000 -nargs 2 -- wpsphoto+.exe @@`

这里需要说明的是fuzz_iterations这个参数，它与afl的fuzz方式不同，winafl特有的持久化fuzz方式在经历特定的fuzz次数后才会关闭进程，所以如果fuzz_iterations这个参数设置的太小的话，会导致持久化fuzz速度降低，如下图所示：

[![](https://p4.ssl.qhimg.com/t0119db7e29f8e99377.png)](https://p4.ssl.qhimg.com/t0119db7e29f8e99377.png)

但是设置太高的话会导致应用程序产生不明原因的崩溃，这和我们所选择的函数也有关联，如果所选的函数不太恰当，例如进行了大量的初始化操作和程序解析文件无关的行为等会导致afl-fuzz无法正常工作，这时我们就必须通过分析、调试来进一步筛选出更合适的函数偏移。合适的函数偏移可以更加高效的进行fuzz，如下图所示：

[![](https://p4.ssl.qhimg.com/t0172d600e2ac69bfcc.png)](https://p4.ssl.qhimg.com/t0172d600e2ac69bfcc.png)

这里需要提到一点，在debug模式下某些函数偏移可能无法正常工作。我最开始猜测是DynamoRIO版本以及sdk的问题，因为在调试过程中发现，就算给了正确的call_convention参数，DynamoRIO依旧无法在迭代测试中正确恢复程序的上下文环境，特别是针对thiscall的调用约定，在利用windbg调试时发现，在所选择的函数地址头部，本该是this指针的ecx寄存器值被赋为0，这导致了内存读取异常，程序崩溃。原因暂时未知，需要进行深入的分析。

[![](https://p3.ssl.qhimg.com/t016d1e0f4fea0865de.png)](https://p3.ssl.qhimg.com/t016d1e0f4fea0865de.png)

### <a class="reference-link" name="%E4%BA%94%E3%80%81%E5%B9%B6%E8%A1%8Cfuzz"></a>五、并行fuzz

和afl一样，winafl同样支持并行fuzz，利用-M(Master) -S(Slave)参数来指定多个fuzzer，但是我这里并没有这么做，因为wps支持多个文件格式，所以我针对不同格式的图片使用了不同的输入、输出文件夹，这样能更快速地确定出问题的文件格式。鉴于之前fuzz的经历，在并行fuzz的时候可能会出现这样一种情况，由于样本不合规范或者其它原因，导致fuzz超时，程序产生hang，这时分发到其它fuzzer的样本中可能也会导致hang，这可能会大大降低fuzz的速度，因此我选择利用多核去fuzz不同格式的样本。



## 分析结果

我在fuzz过程中发现程序出现hang，此时尚不确定是真的hang还是仅仅是超时而已，需要进一步的调试、分析，打开wpsphoto+.exe，在图形界面窗口将样本拖入后发现程序没有响应，进程状况如下：

[![](https://p3.ssl.qhimg.com/t01c66962817d07b055.png)](https://p3.ssl.qhimg.com/t01c66962817d07b055.png)

利用windbg附加调试，查看主线程的调用堆栈：<br><code>0:000&gt; kv<br>
ChildEBP RetAddr  Args to Child<br>
0044c4b8 77235e4c 753dc4fa 000005f4 00000000 ntdll!KiFastSystemCallRet (FPO: [0,0,0])<br>
0044c4bc 753dc4fa 000005f4 00000000 00000000 ntdll!NtReadFile+0xc (FPO: [9,0,0])<br>
0044c520 763a9e12 000005f4 035b0000 00000200 KERNELBASE!ReadFile+0x118 (FPO: [Non-Fpo])<br>
0044c568 7018abd5 000005f4 035b0000 00000200 kernel32!ReadFileImplementation+0xf0 (FPO: [Non-Fpo])<br>
0044c5ac 7018aca0 00000003 035b0000 00000200 MSVCR100!_read_nolock+0x1fa (FPO: [Non-Fpo]) (CONV: cdecl) [f:\dd\vctools\crt_bld\self_x86\crt\src\read.c @ 230]<br>
0044c5f0 7018cdd1 00000003 035b0000 00000200 MSVCR100!_read+0xb7 (FPO: [Non-Fpo]) (CONV: cdecl) [f:\dd\vctools\crt_bld\self_x86\crt\src\read.c @ 92]<br>
0044c608 701930b3 70223068 034382bc 00000000 MSVCR100!_filbuf+0x72 (FPO: [Non-Fpo]) (CONV: cdecl) [f:\dd\vctools\crt_bld\self_x86\crt\src\_filbuf.c @ 136]<br>
0044c630 70192be7 0044c888 ffffffff 00000001 MSVCR100!_fread_nolock_s+0x150 (FPO: [Non-Fpo]) (CONV: cdecl) [f:\dd\vctools\crt_bld\self_x86\crt\src\fread.c @ 268]<br>
0044c678 70192c3c 0044c888 ffffffff 00000001 MSVCR100!fread_s+0x6d (FPO: [Non-Fpo]) (CONV: cdecl) [f:\dd\vctools\crt_bld\self_x86\crt\src\fread.c @ 109]<br>
0044c694 0f930ee3 0044c888 00000001 00000008 MSVCR100!fread+0x18 (FPO: [Non-Fpo]) (CONV: cdecl) [f:\dd\vctools\crt_bld\self_x86\crt\src\fread.c @ 303]<br>
WARNING: Stack unwind information not available. Following frames may be wrong.<br>
0044c6e0 0f969fbc 0044c888 00000008 71fb1f43 photo!IKAuthorizationHandler::operator=+0x2f53<br>
0044c8a0 0f7725a6 71fb1ebb 0212482c 020a68f0 photo!ImageWrapper::saveIndex+0x3207c<br>
0044c958 0f772f07 0044c984 71fb1e77 0212482c photo!ImageWrapper::getExifData+0x1d6<br>
0044c994 0f77f020 035dfaa0 0338ca10 0044c9dc photo!ImageWrapper::init+0x87<br>
0044c9fc 0f77f273 0044ca30 0044ca2c 71fb1dab photo!ImageWrapper::load+0xc010<br>
0044ca48 0f77d2dc 035e1d00 020a6160 0044ca6c photo!ImageWrapper::load+0xc263<br>
0044ca58 0f82bce3 035e1db4 020a6160 0044cb14 photo!ImageWrapper::load+0xa2cc<br>
0044ca6c 0f7566f5 035e1db4 0000001d 020a6160 photo!ImageView::resizeEvent+0x2973<br>
0044ca84 66ea3cdc 00000000 00000019 0044cb14 photo!FullScreenView::metaObject+0x9e5<br>
0044ca98 66ec240b 020a6160 00000000 0000001d QtCore4!QMetaObject::metacall+0x3c<br>
0044cafc 0f74b6e5 020de240 01bbd7e8 02090238 QtCore4!QMetaObject::activate+0x2ab<br>
0044cb1c 0f753bcd 035e1db4 0000000c 020de240 photo!PhotoMainWindow::signals_resizeWindow+0x275<br>
0044cb3c 66ea3cdc 00000000 0000000c 0044cbcc photo!PhotoMainWindow::qt_metacall+0x34d<br>
······</code>

在ida中查看相应的函数，发现关键函数sub_10249DC0包含如下代码：

[![](https://p3.ssl.qhimg.com/t019a24bee8a899beec.png)](https://p3.ssl.qhimg.com/t019a24bee8a899beec.png)

这可能是导致死循环的关键，需要进行深入的分析。查看两个虚函数的调用，分别调用了ferror以及feof函数，且均返回0。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t017f5825f06865bdfe.png)

接下来又是一处虚函数调用，调用的是sub_10210CA0函数，该函数主要调用了fseek函数，对文件指针进行重新定位，如下：

<code>int __thiscall sub_10210CA0(_DWORD *this, int a2, int a3, int a4)<br>
`{`<br>
int v4; // esi<br>
_DWORD *v5; // edi<br>
int v6; // eax<br>
​<br>
v4 = 0;<br>
v5 = this;<br>
if ( a4 )<br>
`{`<br>
if ( a4 == 1 )<br>
`{`<br>
v4 = 1;<br>
`}`<br>
else if ( a4 == 2 )<br>
`{`<br>
v4 = 2;<br>
`}`<br>
`}`<br>
else<br>
`{`<br>
v4 = 0;<br>
`}`<br>
v6 = this[1];<br>
if ( *(_DWORD *)(v6 + 0x5C) != 2 )<br>
`{`<br>
*(_DWORD *)(v6 + 0x5C) = 2;<br>
fseek(*(FILE **)(v6 + 88), 0, 1);<br>
`}`<br>
return fseek(*(FILE **)(v5[1] + 88), a2, v4);<br>
`}`</code>

这里比较可疑的是第二个fseek，其中的offset参数是上层函数传入的参数，调试时的数据如下：

[![](https://p1.ssl.qhimg.com/t014b2b6daca64a3d30.png)](https://p1.ssl.qhimg.com/t014b2b6daca64a3d30.png)

可以看出，第二个fseek传入的参数有较大问题，第一个参数是被读取文件的FILE指针，第二个参数offset是0xfffffff8。而根据fseek函数的说明，该参数可以是负数。这意味着读取文件后，本来向后移动的文件流指针又被移动到了读取前的位置，造成下次调用fread函数时依旧读取相同位置的数据，这就造成了一个死循环，导致应用程序dos。而0xfffffff8这个值是读取的文件的内容，程序并没有对这个做检查，导致造成dos，所以我们应对该值做出判断，判断偏移是否为负数，如果是负数，则终止对文件的解析。

整个漏洞挖掘过程就到此为止，后续我会为大家介绍对其它软件的漏洞挖掘与分析过程，敬请期待。

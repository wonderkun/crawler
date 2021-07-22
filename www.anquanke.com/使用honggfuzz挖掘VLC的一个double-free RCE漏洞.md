> 原文链接: https://www.anquanke.com//post/id/181017 


# 使用honggfuzz挖掘VLC的一个double-free RCE漏洞


                                阅读量   
                                **254520**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Symeon Paraschoudis，文章来源：Symeon Paraschoudis
                                <br>原文地址：[https://www.pentestpartners.com/security-blog/double-free-rce-in-vlc-a-honggfuzz-how-to/](https://www.pentestpartners.com/security-blog/double-free-rce-in-vlc-a-honggfuzz-how-to/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t013635f848548860af.jpg)](https://p5.ssl.qhimg.com/t013635f848548860af.jpg)



## 介绍

本文将介绍我如何使用Honggfuzz对VLC进行漏洞挖掘。我首先对Honggfuzz进行了一些设置以便于VLC的漏洞挖掘进行，最终花费了三个月的时间挖掘出了五个漏洞，其中一个是高危的double-free 漏洞，其CVE编号为CVE-2019-12874.

这是VLC项目对于CVE-2019-12874发布的安全公告：[https://www.videolan.org/security/sa1901.html。](https://www.videolan.org/security/sa1901.html%E3%80%82)

下面将详细介绍我如何挖掘出该漏洞，希望对你有所启发并带领你进入fuzz挖掘之路



## 1.相关背景介绍

### <a class="reference-link" name="VLC"></a>VLC

VLC是一个免费的媒体播放器，是由VideoLAN项目开发的开源，便携，跨平台和流媒体服务器。像VLC这样的媒体播放器通常具有非常复杂的代码库，包括解析和支持大量文件媒体文件格式，数学计算，编解码器，解复用器，文本渲染器和更复杂的代码。

[![](https://p1.ssl.qhimg.com/t017e865d54781ccf57.png)](https://p1.ssl.qhimg.com/t017e865d54781ccf57.png)

### <a class="reference-link" name="honggfuzz"></a>honggfuzz

honggfuzz是一个现代化，基于代码覆盖率的反馈驱动fuzzer，其作者为Robert Swiecki。<br>
（反馈驱动：通过监控样本触发的代码覆盖率，进而改进输入样本以提高代码覆盖率，增加发现漏洞的概率）

**为何选择honggfuzz？**

它提供了一种简单的方法来检测目标（但是原生版本的honggfuzz不适用于VLC，本文将会介绍我如何改造它使其适用于VLC的漏洞挖掘），它有一些非常强大的命令，比如它可以只改变X个字节数量（使用 -F 参数），它具有一个易于使用的命令行，它使用AddressSanitzer工具进行代码覆盖率测试，因此可以保存所有特别的崩溃点以及命中新代码块的覆盖文件。

在不应用代码覆盖率测试的情况下发现这些错误是非常困难的，因为考虑到代码的复杂性，一些路径可能永远无法被触及到。



## 2.获取并构建VLC

VLC依赖于许多库和外部项目。在Ubuntu系统上，只需通过apt获取所有依赖项即可轻松解决：

```
$ apt-get build-dep vlc
```

（如果你使用的是ubuntu系统，请确保安装了libxcb-xkb-dev）。下面我将进行获取源代码的操作，注意请获取最新版本的代码。

运行bootstrap，它将为我们的平台生成makefile。

```
$ git clone https://github.com/videolan/vlc 
$ ./bootstrap
```

完成操作后，我还想添加其对AddressSanitizer的支持。但是单纯的在configure命令后添加-with-sanitizer = address是不够的，因为它会在编译完成之前由于缺少编译标志而产生错误。因此，我需要回滚到以下commit，因此我可以成功编译VLC并添加AddressSanitizer工具。

```
$ git revert e85682585ab27a3c0593c403b892190c52009960
```



## 3.获取样本

首先，我需要获取一些优质的视频样本。幸运的是，FFmpeg测试套件([https://samples.ffmpeg.org/)有大量不错的样本，我们可以直接使用当中的样本。对于第一次尝试，我尝试对mkv格式进行测试，通过下面的命令进行样本获取：](https://samples.ffmpeg.org/)%E6%9C%89%E5%A4%A7%E9%87%8F%E4%B8%8D%E9%94%99%E7%9A%84%E6%A0%B7%E6%9C%AC%EF%BC%8C%E6%88%91%E4%BB%AC%E5%8F%AF%E4%BB%A5%E7%9B%B4%E6%8E%A5%E4%BD%BF%E7%94%A8%E5%BD%93%E4%B8%AD%E7%9A%84%E6%A0%B7%E6%9C%AC%E3%80%82%E5%AF%B9%E4%BA%8E%E7%AC%AC%E4%B8%80%E6%AC%A1%E5%B0%9D%E8%AF%95%EF%BC%8C%E6%88%91%E5%B0%9D%E8%AF%95%E5%AF%B9mkv%E6%A0%BC%E5%BC%8F%E8%BF%9B%E8%A1%8C%E6%B5%8B%E8%AF%95%EF%BC%8C%E9%80%9A%E8%BF%87%E4%B8%8B%E9%9D%A2%E7%9A%84%E5%91%BD%E4%BB%A4%E8%BF%9B%E8%A1%8C%E6%A0%B7%E6%9C%AC%E8%8E%B7%E5%8F%96%EF%BC%9A)

```
$ wget -r https://samples.ffmpeg.org/ -A mkv
```

[![](https://p3.ssl.qhimg.com/t0102093f767ab827af.png)](https://p3.ssl.qhimg.com/t0102093f767ab827af.png)

一旦拥有相当数量的样本，下一步就是限制样本的大小，比如限制样本的大小小于5mb：

```
$ find . -name "*.mkv" -type f -size -5M -exec mv -f `{``}` ~/Desktop/mkv_samples/ ;
```



## 4.样本代码覆盖率测试（使用GCC）

在我们得到样本之后，我们需要验证我们的初始种子能否给我们提供不错的代码覆盖率：代码覆盖率越大，我们找到bug的可能性就越大。

让我们使用GCC的coverage标志来编译VLC：

```
$ CC = gcc CXX = g ++ ./configure --enable-debug --enable-coverage 
$ make -j8
```

编译成功后，我们可以确认是否有gcno文件：

```
$ find . -name *.gcno
```

在这个阶段，我们准备逐个运行我们的种子文件并以此生成相关图表帮助我们进行分析。根据样本和电影的长度，我们需要找出一种方法来播放X秒并正常地退出VLC，否则我们将会在样本的播放上花费大量不必要的时间。

幸运的是，VLC已经有以下两个参数：-play-and-exit和-run-time = n（n的单位是秒）。所以我们将cd 到我们的samples文件夹并运行以下这个bash脚本：

```
#!/bin/bash
FILES=/home/symeon/Desktop/vlc_samples-master/honggfuzz_coverage/*.mkv
for f in $FILES
do
 echo "[*] Processing $f file..."
 ASAN_OPTIONS=detect_leaks=0 timeout 5 ./vlc-static --play-and-exit --run-time=5 "$f"
done
```

执行脚本后，你会看到VLC播放5秒钟，退出然后逐个循环播放视频。接下来，我们将使用[@ea_foundation](https://github.com/ea_foundation)编写的小工具covnavi([https://github.com/Cisco-Talos/covnavi/)，它可以获取所有的覆盖信息并为你完成所有繁重的任务。](https://github.com/Cisco-Talos/covnavi/)%EF%BC%8C%E5%AE%83%E5%8F%AF%E4%BB%A5%E8%8E%B7%E5%8F%96%E6%89%80%E6%9C%89%E7%9A%84%E8%A6%86%E7%9B%96%E4%BF%A1%E6%81%AF%E5%B9%B6%E4%B8%BA%E4%BD%A0%E5%AE%8C%E6%88%90%E6%89%80%E6%9C%89%E7%B9%81%E9%87%8D%E7%9A%84%E4%BB%BB%E5%8A%A1%E3%80%82)

[![](https://p2.ssl.qhimg.com/t013dddb0ec4ffb564f.png)](https://p2.ssl.qhimg.com/t013dddb0ec4ffb564f.png)

在图3中可以看到，在使用gcov后，将会在本地生成一些新的文件夹web。打开当中的index.html文件，并导航到demux/mkv下查看初始覆盖率。通过我们的基本样本集，我们击中了45.1％的运行线路和33.9％的函数！

[![](https://p5.ssl.qhimg.com/t01495f08afb9ff4f31.png)](https://p5.ssl.qhimg.com/t01495f08afb9ff4f31.png)

至此我们拥有了足够大的代码覆盖率，下面将进入fuzzing环节。



## 5.测试示例

在搜索文档时，发现VLC提供了一个示例API代码([https://wiki.videolan.org/LibVLC_Tutorial/)，可用于播放媒体文件几秒钟，然后关闭播放器。](https://wiki.videolan.org/LibVLC_Tutorial/)%EF%BC%8C%E5%8F%AF%E7%94%A8%E4%BA%8E%E6%92%AD%E6%94%BE%E5%AA%92%E4%BD%93%E6%96%87%E4%BB%B6%E5%87%A0%E7%A7%92%E9%92%9F%EF%BC%8C%E7%84%B6%E5%90%8E%E5%85%B3%E9%97%AD%E6%92%AD%E6%94%BE%E5%99%A8%E3%80%82)

这正是我们需要的工具。他们还提供了一个VLC所有模块的详细列表，可在此处查询([https://www.videolan.org/developers/vlc/doc/doxygen/html/modules.html](https://www.videolan.org/developers/vlc/doc/doxygen/html/modules.html))

```
#include &lt;stdio.h&gt;
#include &lt;stdlib.h&gt;
#include &lt;vlc/vlc.h&gt;

int main(int argc, char* argv[])
`{`
   libvlc_instance_t * inst;
   libvlc_media_player_t *mp;
   libvlc_media_t *m;

   if(argc &lt; 2)
   `{`
   printf("usage: %s &lt;input&gt;n", argv[0]);
   return 0;
   `}`
   /* Load the VLC engine */
   inst = libvlc_new (0, NULL);

   /* Create a new item */
   m = libvlc_media_new_path (inst, argv[1]);

   /* Create a media player playing environement */
   mp = libvlc_media_player_new_from_media (m);

   /* No need to keep the media now */
   libvlc_media_release (m);

   /* play the media_player */
   libvlc_media_player_play (mp);

   sleep (2); /* Let it play a bit */

   /* Stop playing */
   libvlc_media_player_stop (mp);

   /* Free the media_player */
   libvlc_media_player_release (mp);

   libvlc_release (inst);

   return 0;

`}`
```

为了编译上述代码，我们需要链接我们新编译的库。导航到/etc/ld.so.conf.d，创建一个新文件libvlc.conf并包含liblvc的路径：

```
/home/symeon/vlc-coverage/lib/.libs
```

确保执行这条命令来更新ldconfig

```
ldconfig
```

现在让我们使用我们的新编译的库来编译该代码并将其链接到ASAN。

```
hfuzz-clang harness.c -I/home/symeon/Desktop/vlc/include -L/home/symeon/Desktop/vlc/lib/.libs -o harness -lasan -lvlc
```

编译完成后执行它，不幸的是，这将导致以下崩溃，使其无法用于我们的模糊测试：

[![](https://p3.ssl.qhimg.com/t018b4e4ce5412b2d74.png)](https://p3.ssl.qhimg.com/t018b4e4ce5412b2d74.png)

有趣的是，通过安装libvlc-dev库并链接到这个库，该代码将成功执行，但这对我们完成目标没有作用，因为没有产生任何的覆盖。在下一步中，尝试使用clang来检测整个VLC二进制文件！



## 6.使用honggfuzz检测VLC（clang coverage）

由于我们之前的方法不起作用，让我们尝试编译VLC并使用honggfuzz进行检测尝试。我将使用最新的clang以及编译器-rt运行时库，它增加了对代码覆盖的支持。

```
$:~/vlc-coverage/bin$ clang --version
clang version 9.0.0 (https://github.com/llvm/llvm-project.git 281a5beefa81d1e5390516e831c6a08d69749791)
Target: x86_64-unknown-linux-gnu
Thread model: posix
InstalledDir: /home/symeon/Desktop/llvm-project/build/bin
```

遵循honggfuzz的反馈驱动指令，我们需要运行以下命令并启用AddressSanitizer：

```
$ export CC=/home/symeon/Desktop/honggfuzz/hfuzz_cc/hfuzz-clang
$ export CXX=/home/symeon/Desktop/honggfuzz/hfuzz_cc/hfuzz-clang++
$ ./configure --enable-debug --with-sanitizer=address
```

配置成功后，我们尝试编译它：

```
$ make -j4
```

但是一段时间后，编译失败了：

```
&lt;scratch space&gt;:231:1: note: expanded from here
VLC_COMPILER
^
../config.h:785:34: note: expanded from macro 'VLC_COMPILER'
#define VLC_COMPILER " "/usr/bin/ld" -z relro --hash-style=gnu --eh-frame-hdr -m elf_x86_64 -dynamic-linker /lib64/ld-linux-x86-64.so.2 -o  a.o...

                                  ^

3 errors generated.
make[3]: *** [Makefile:3166: version.lo] Error 1
make[3]: *** Waiting for unfinished jobs....
make[3]: Leaving directory '/home/symeon/vlc-cov/covnavi/vlc/src'
make[2]: *** [Makefile:2160: all] Error 2
make[2]: Leaving directory '/home/symeon/vlc-cov/covnavi/vlc/src'
make[1]: *** [Makefile:1567: all-recursive] Error 1
make[1]: Leaving directory '/home/symeon/vlc-cov/covnavi/vlc'
make: *** [Makefile:1452: all] Error 2
```

查看config.log，我们可以看到以下内容：

```
#define VLC_COMPILE_BY "symeon"
#define VLC_COMPILE_HOST "ubuntu"
#define VLC_COMPILER " "/usr/bin/ld" -z relro --hash-style=gnu --eh-frame-hdr -m elf_x86_64 -dynamic-linker /lib64/ld-linux-x86-64.so.2 -o a.out  /usr/lib/gcc/x86_64-linux-gnu/8/../../../x86_64-linux-gnu/crt1.o /usr/lib/gcc/x86_64-linux-gnu/8/../../../x86_64-linux-gnu/crti.o  /usr/lib/gcc/x86_64-linux-gnu/8/crtbegin.o -L/usr/lib/gcc/x86_64-linux-gnu/8 -L/usr/lib/gcc/x86_64-linux-gnu/8/../../../x86_64-linux-gnu -L/lib/x86_64-linux-gnu -L/lib/../lib64 -L/usr/lib/x86_64-linux-gnu -L/usr/lib/gcc/x86_64-linux-gnu/8/../../.. -L/home/symeon/Desktop/llvm-project/build/bin/../lib -L/lib -L/usr/lib --whole-archive /home/symeon/Desktop/llvm-project/build/lib/clang/9.0.0/lib/linux/libclang_rt.ubsan_standalone-x86_64.a --no-whole-archive --dynamic-list=/home/symeon/Desktop/llvm-project/build/lib/clang/9.0.0/lib/linux/libclang_rt.ubsan_standalone-x86_64.a.syms --wrap=strcmp --wrap=strcasecmp --wrap=strncmp --wrap=strncasecmp --wrap=strstr --wrap=strcasestr --wrap=memcmp --wrap=bcmp --wrap=memmem --wrap=strcpy --wrap=ap_cstr_casecmp --wrap=ap_cstr_casecmpn --wrap=ap_strcasestr --wrap=apr_cstr_casecmp --wrap=apr_cstr_casecmpn --wrap=CRYPTO_memcmp --wrap=OPENSSL_memcmp --wrap=OPENSSL_strcasecmp --wrap=OPENSSL_strncasecmp --wrap=memcmpct --wrap=xmlStrncmp --wrap=xmlStrcmp --wrap=xmlStrEqual --wrap=xmlStrcasecmp --wrap=xmlStrncasecmp --wrap=xmlStrstr --wrap=xmlStrcasestr --wrap=memcmp_const_time --wrap=strcsequal -u HonggfuzzNetDriver_main -u LIBHFUZZ_module_instrument -u LIBHFUZZ_module_memorycmp /tmp/libhfnetdriver.1000.419f7f6c4058b450.a /tmp/libhfuzz.1000.746a32a18d2c8f8a.a /tmp/libhfnetdriver.1000.419f7f6c4058b450.a --no-as-needed -lpthread -lrt -lm -ldl -lgcc --as-needed -lgcc_s --no-as-needed -lpthread -lc -lgcc --as-needed -lgcc_s --no-as-needed /usr/lib/gcc/x86_64-linux-gnu/8/crtend.o /usr/lib/gcc/x86_64-linux-gnu/8/../../../x86_64-linux-gnu/crtn.o"
```

显然，VLC_COMPILER变量被破坏了，因此检测失败。我们不要放弃，并使用以下命令继续编译：

```
$ make clean
$ CC=clang CXX=clang++ CFLAGS="-fsanitize-coverage=trace-pc-guard,indirect-calls,trace-cmp" CXXFLAGS="-fsanitize-coverage=trace-pc-guard,indirect-calls,trace-cmp" ./configure --enable-debug --with-sanitizer=address
$ ASAN_OPTIONS=detect_leaks=0 make -j8
```

会给我们以下输出：

```
GEN      ../modules/plugins.dat
make[2]: Leaving directory '/home/symeon/vlc-cov/covnavi/vlc/bin'
Making all in test
make[2]: Entering directory '/home/symeon/vlc-cov/covnavi/vlc/test'
make[2]: Nothing to be done for 'all'.
make[2]: Leaving directory '/home/symeon/vlc-cov/covnavi/vlc/test'
make[2]: Entering directory '/home/symeon/vlc-cov/covnavi/vlc'
  GEN      cvlc
  GEN      rvlc
  GEN      nvlc
  GEN      vlc
make[2]: Leaving directory '/home/symeon/vlc-cov/covnavi/vlc'
make[1]: Leaving directory '/home/symeon/vlc-cov/covnavi/vlc'
```

现在虽然编译成功，但二进制文件缺少honggfuzz的工具。因此，我们需要删除现有的vlc_static二进制文件，并手动将其与libhfuzz库链接。为此，我们需要弄清楚在哪里进行的链接。让我们删除vlc-static二进制文件：

```
$ cd bin
$ rm vlc-static
```

并在编译/链接vlc-binary时运行strace：

```
$ ASAN_OPTIONS=detect_leaks=0 strace -s 1024 -f -o compilation_flags.log make
CCLD     vlc-static
GEN      ../modules/plugins.dat
```

上面的命令，将最大字符串大小指定为1024个字符（默认为32），并将所有输出保存到指定文件。打开日志文件并查找“-o vlc-static” 会给我们以下结果：

```
-- snip --
103391 &lt;... wait4 resumed&gt; [`{`WIFEXITED(s) &amp;&amp; WEXITSTATUS(s) == 0`}`], 0, NULL) = 103392
103391 rt_sigprocmask(SIG_BLOCK, [HUP INT QUIT TERM XCPU XFSZ], NULL, 8) = 0
103391 vfork( &lt;unfinished ...&gt;
103393 rt_sigprocmask(SIG_SETMASK, [], NULL, 8) = 0
103393 prlimit64(0, RLIMIT_STACK, `{`rlim_cur=8192*1024, rlim_max=RLIM64_INFINITY`}`, NULL) = 0
103393 execve("/bin/bash", ["/bin/bash", "-c", "echo "  CCLD    " vlc-static;../doltlibtool --silent --tag=CC   --mode=link clang  - DTOP_BUILDDIR=\"$(cd ".."; pwd)\" -DTOP_SRCDIR=\"$(cd ".."; pwd)\"  -fsanitize-coverage=trace-pc-guard,indirect-calls,trace-cmp   -Werror=unknown-warning-option -Werror=invalid-command-line-argument -pthread -Wall -Wextra -Wsign-compare -Wundef -Wpointer-arith -Wvolatile-register-var -Wformat -Wformat-security -Wbad-function-cast -Wwrite-strings -Wmissing-prototypes -Werror-implicit-function-declaration -Winit-self -pipe -fvisibility=hidden -fsanitize=address -g -fsanitize-address-use-after-scope -fno-omit-frame-pointer -fno-math-errno -funsafe-math-optimizations -funroll-loops -fstack-protector-strong  -no-install -static -fsanitize=address -o vlc-static vlc_static-vlc.o vlc_static-override.o ../lib/libvlc.la    "], 0x5565fb56ae10 /* 59 vars */ &lt;unfinished ...&gt;
103391 &lt;... vfork resumed&gt; )            = 103393
103391 rt_sigprocmask(SIG_UNBLOCK, [HUP INT QUIT TERM XCPU XFSZ], NULL, 8) = 0
103391 wait4(-1,  &lt;unfinished ...&gt;
103393 &lt;... execve resumed&gt; )           = 0
103393 brk(NULL)                        = 0x557581212000
```

我们设法找到了vlc-static所需的编译标志和库。最后一步是通过发出以下命令链接libhfuzz.a的库：

```
$ ~/vlc-coverage/bin$ ../doltlibtool --tag=CC --mode=link clang -DTOP_BUILDDIR="/home/symeon/vlc-coverage" -DTOP_SRCDIR="/home/symeon/vlc-coverage" -fsanitize-coverage=trace-pc-guard,trace-cmp -Werror=unknown-warning-option -Werror=invalid-command-line-argument -pthread -Wall -Wextra -Wsign-compare -Wundef -Wpointer-arith -Wvolatile-register-var -Wformat -Wformat-security -Wbad-function-cast -Wwrite-strings -Wmissing-prototypes -Werror-implicit-function-declaration -Winit-self -pipe -fvisibility=hidden -fsanitize=address -g -fsanitize-address-use-after-scope -fno-omit-frame-pointer -fno-math-errno -funsafe-math-optimizations -funroll-loops -fstack-protector-strong -no-install -static  -o vlc-static vlc_static-vlc.o vlc_static-override.o ../lib/libvlc.la -Wl,--whole-archive -L/home/symeon/Desktop/honggfuzz/libhfuzz/ -lhfuzz -u,LIBHFUZZ_module_instrument -u,LIBHFUZZ_module_memorycmp -Wl,--no-whole-archive
```

最后一步，让我们确认这次生成的vlc_static二进制文件包含libhfuzz的标志：

```
$ ~/vlc-coverage/bin$ nm vlc-static | grep LIBHFUZZ

```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01fa86bc3ee6988f84.png)



## 7.进行模糊测试

在这部分中，我们将使用一个具有100GB RAM和8个内核的VM。

[![](https://p3.ssl.qhimg.com/t01002b1a7e1df9dd5f.png)](https://p3.ssl.qhimg.com/t01002b1a7e1df9dd5f.png)

将用于检测的二进制工具vlc_static复制到我们的ramdisk(/run/shm)上，然后复制样本并开始模糊测试

```
$ cp ./vlc-static /run/shm
$ cp -r ./mkv_samples /run/shm
```

在下面的命令中，-f是包含我们样本的文件夹，-F将限制为最大16kB。

```
$ honggfuzz -f mkv_samples -t 5 -F 16536 -- ./vlc-static --play-and-exit --run-time=4 ___FILE____
```

如果一切顺利，你应该获得edge和PC的大量覆盖信息，如下面的屏幕截图所示：

[![](https://p2.ssl.qhimg.com/t0187d5070ee87b416b.png)](https://p2.ssl.qhimg.com/t0187d5070ee87b416b.png)

一般来说，在几个小时内你可以得到你的第一次崩溃，可以在执行honggfuzz的同一目录（默认目录）中找到崩溃以及相应的文本文件HONGGFUZZ.REPORT.TXT，其中包含honggfuzz参数，崩溃日期等信息，故障指令以及堆栈跟踪。

[![](https://p0.ssl.qhimg.com/t018d13f928ecb4f686.png)](https://p0.ssl.qhimg.com/t018d13f928ecb4f686.png)



## 8.崩溃结果分析

经过三天的模糊测试，honggfuzz发现了一些有趣的崩溃，如SIGSEV，SIGABRT和SIGPFPE。

尽管其名称为SIGABRT，但在AddressSanitizer下运行crashers（我们已经对VLC进行了检测）显示这些错误实际上主要是基于堆的越界读取漏洞。我们可以使用这个简单的bash脚本使用之前检测的二进制文件循环遍历crashers：

```
$ cat asan_triage.sh
 #!/bin/bash
 FILES=/home/symeon/Desktop/crashers/*
 OUTPUT=asan.txt
 for f in $FILES
 do
 echo "[*] Processing $f file..." &gt;&gt; $OUTPUT 2&gt;&amp;1
 ASAN_OPTIONS=detect_leaks=0,verbosity=1 timeout 12 ./vlc-static --play-and-exit --run-time=10
"$f"  &gt;&gt;$OUTPUT 2&gt;&amp;1
done
```

[![](https://p5.ssl.qhimg.com/t017b18120caf3c6ccc.png)](https://p5.ssl.qhimg.com/t017b18120caf3c6ccc.png)

一旦运行它，将不会看到任何输出，因为我们将所有输出/错误重定向到文件asan.txt。打开此文件，它会显示崩溃的根本原因，以及发生崩溃的符号化堆栈跟踪，如下所示

```
$ cat asan.txt | grep AddressSanitizer -A 5
==59237==ERROR: AddressSanitizer: attempting free on address which was not malloc()-ed: 0x02d000000000 in thread T5
#0 0x4ac420 in __interceptor_free /home/symeon/Desktop/llvm-project/compiler-rt/lib/asan/asan_malloc_linux.cc:123:3
#1 0x7f674f0e8610 in es_format_Clean /home/symeon/Desktop/vlc/src/misc/es_format.c:496:9
#2 0x7f672fde9dac in mkv::mkv_track_t::~mkv_track_t() /home/symeon/Desktop/vlc/modules/demux/mkv/mkv.cpp:892:5
#3 0x7f672fc3f494 in std::default_delete&lt;mkv::mkv_track_t&gt;::operator()(mkv::mkv_track_t*) const /usr/lib/gcc/x86_64-linux- gnu/8/../../../../include/c++/8/bits/unique_ptr.h:81:2
#4 0x7f672fc3f2d0 in std::unique_ptr&lt;mkv::mkv_track_t, std::default_delete&lt;mkv::mkv_track_t&gt; &gt;::~unique_ptr() /usr/lib/gcc/x86_64-linux-  gnu/8/../../../../include/c++/8/bits/unique_ptr.h:274:4
--
SUMMARY: AddressSanitizer: bad-free /home/symeon/Desktop/llvm-project/compiler-rt/lib/asan/asan_malloc_linux.cc:123:3 in __interceptor_free
Thread T5 created by T4 here:
#0 0x444dd0 in __interceptor_pthread_create /home/symeon/Desktop/llvm-project/compiler-rt/lib/asan/asan_interceptors.cc:209:3
#1 0x7f674f15b6a1 in vlc_clone_attr /home/symeon/Desktop/vlc/src/posix/thread.c:421:11
#2 0x7f674f15b0ca in vlc_clone /home/symeon/Desktop/vlc/src/posix/thread.c:433:12
#3 0x7f674ef6e141 in input_Start /home/symeon/Desktop/vlc/src/input/input.c:200:25
--
==59286==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x602000041fa0 at pc 0x7fabef0d00a7 bp 0x7fabf7074bd0 sp 0x7fabf7074bc8
READ of size 8 at 0x602000041fa0 thread T5
#0 0x7fabef0d00a6 in mkv::demux_sys_t::FreeUnused() /home/symeon/Desktop/vlc/modules/demux/mkv/demux.cpp:267:34
#1 0x7fabef186e6e in mkv::Open(vlc_object_t*) /home/symeon/Desktop/vlc/modules/demux/mkv/mkv.cpp:257:12
#2 0x7fac0e2b01b4 in demux_Probe /home/symeon/Desktop/vlc/src/input/demux.c:180:15
#3 0x7fac0e1f82b7 in module_load /home/symeon/Desktop/vlc/src/modules/modules.c:122:15
--
SUMMARY: AddressSanitizer: heap-buffer-overflow /home/symeon/Desktop/vlc/modules/demux/mkv/demux.cpp:267:34 in mkv::demux_sys_t::FreeUnused()
Shadow bytes around the buggy address:
0x0c04800003a0: fa fa fd fd fa fa fd fd fa fa fd fd fa fa fd fd
0x0c04800003b0: fa fa fd fd fa fa fd fd fa fa fd fd fa fa fd fd
0x0c04800003c0: fa fa fd fd fa fa 00 02 fa fa fd fd fa fa fd fd
0x0c04800003d0: fa fa fd fd fa fa fd fd fa fa fd fd fa fa 00 00
--
==59343==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x6250016a7a4f at pc 0x0000004ab6da bp 0x7f75e5457b10 sp 0x7f75e54572c0
READ of size 128 at 0x6250016a7a4f thread T15
#0 0x4ab6d9 in __asan_memcpy /home/symeon/Desktop/llvm-project/compiler-rt/lib/asan/asan_interceptors_memintrinsics.cc:22:3
#1 0x7f75ece563c2 in lavc_CopyPicture /home/symeon/Desktop/vlc/modules/codec/avcodec/video.c:435:13
#2 0x7f75ece52ac3 in DecodeBlock /home/symeon/Desktop/vlc/modules/codec/avcodec/video.c:1257:17
#3 0x7f75ece4d587 in DecodeVideo /home/symeon/Desktop/vlc/modules/codec/avcodec/video.c:1354:12
--
SUMMARY: AddressSanitizer: heap-buffer-overflow /home/symeon/Desktop/llvm-project/compiler-rt/lib/asan/asan_interceptors_memintrinsics.cc:22:3  in __asan_memcpy
Shadow bytes around the buggy address:
0x0c4a802ccef0: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
0x0c4a802ccf00: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
0x0c4a802ccf10: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
0x0c4a802ccf20: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
--
==59411==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x6040000716b4 at pc 0x0000004ab6da bp 0x7f97b4ea8290 sp 0x7f97b4ea7a40
READ of size 13104 at 0x6040000716b4 thread T5
#0 0x4ab6d9 in __asan_memcpy /home/symeon/Desktop/llvm-project/compiler-rt/lib/asan/asan_interceptors_memintrinsics.cc:22:3
#1 0x7f97aceb2858 in mkv::matroska_segment_c::TrackInit(mkv::mkv_track_t*)::TrackCodecHandlers::StringProcessor_1783_handler(char const*&amp;,  mkv::matroska_segment_c::TrackInit(mkv::mkv_track_t*)::HandlerPayload&amp;)  /home/symeon/Desktop/vlc/modules/demux/mkv/matroska_segment_parse.cpp:1807:25
#2 0x7f97aceb1e7b in mkv::matroska_segment_c::TrackInit(mkv::mkv_track_t*)::TrackCodecHandlers::StringProcessor_1783_callback(char const*,  void*) /home/symeon/Desktop/vlc/modules/demux/mkv/matroska_segment_parse.cpp:1783:9
#3 0x7f97ace4ed16 in (anonymous namespace)::StringDispatcher::send(char const* const&amp;, void* const&amp;) const   /home/symeon/Desktop/vlc/modules/demux/mkv/string_dispatcher.hpp:128:13
--
SUMMARY: AddressSanitizer: heap-buffer-overflow /home/symeon/Desktop/llvm-project/compiler-rt/lib/asan/asan_interceptors_memintrinsics.cc:22:3  in __asan_memcpy
Shadow bytes around the buggy address:
0x0c0880006280: fa fa fd fd fd fd fd fd fa fa fd fd fd fd fd fd
0x0c0880006290: fa fa fd fd fd fd fd fd fa fa fd fd fd fd fd fd
0x0c08800062a0: fa fa fd fd fd fd fd fd fa fa 00 00 00 00 00 02
0x0c08800062b0: fa fa 00 00 00 00 04 fa fa fa 00 00 00 00 00 04
```

至此我们拥有了PoC，以及显著的符号化痕迹，可以发现发生崩溃的地点。



## 9.改善覆盖范围

默认情况下，Honggfuzz会将生成新coverage的所有新样本保存到我们样本的同一文件夹中（可以通过-covdir_all参数进行修改）。虽然我们在最初的模糊测试中发现了一些漏洞，但是我们应该重新运行honggfuzz获取覆盖信息，看看honggfuzz找不到哪些不同点（也就是魔术值，也许是crc校验和或字符串比较）。

在本例中，我将重新运行先前的bash脚本来提供所有* .cov文件。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01c6d520bbe89b05aa.png)

如图所示，在生成新路径时共保存了86254个文件。

现在是时候再次遍历这些文件：

[![](https://p4.ssl.qhimg.com/t01f330b4d86e688774.png)](https://p4.ssl.qhimg.com/t01f330b4d86e688774.png)

让我们重新运行生成新coverage，看看我们命中了多少代码。

[![](https://p2.ssl.qhimg.com/t01bc88cd68ea891e94.png)](https://p2.ssl.qhimg.com/t01bc88cd68ea891e94.png)

因此，经过三天的模糊测试，我们将整体覆盖率从45.1％略微提升至50％！注意Ebml_parser.cpp从最初的71.5％增加到96.8％，实际上我们能够在对.mkv文件模糊测试的同时找到EBML解析功能的一些错误！

我们接下来的步骤是什么？我们如何改善我们的覆盖范围？在手动检查覆盖范围之后，结果发现诸如void matroska_segment_c :: ParseAttachments（KaxAttachments * attachments）之类的函数从未被命中。

[![](https://p4.ssl.qhimg.com/t010588b26b9f78da82.png)](https://p4.ssl.qhimg.com/t010588b26b9f78da82.png)

经过一些调研，我们发现名为mkvpropedit的工具可用于向我们的示例文件添加一些附件（在视频中添加一帧）。试试看：

```
$ mkvpropedit SampleVideo_720x480_5mb.mkv --add-attachment '/home/symeon/Pictures/Screenshot from 2019-03-24 11-47-04.png'
```

[![](https://p0.ssl.qhimg.com/t01c1b5abecdda75869.png)](https://p0.ssl.qhimg.com/t01c1b5abecdda75869.png)

这看起来很有效！最后让我们通过在相关代码上设置断点来确认它，并使用新样本运行VLC：

[![](https://p3.ssl.qhimg.com/t0108270351a147cc85.png)](https://p3.ssl.qhimg.com/t0108270351a147cc85.png)

我们成功地创建了一个新的附件并在mkv :: matroska_segment代码库中命中了新的函数！我们的下一步将重复应用这项技术，调整样品并重新对我们的目标进行模糊测试。



## 10.发现的漏洞

运行我们的模糊测试项目两周后，从下面的屏幕截图中可以看出，我们执行次数总计100万次，导致1547次崩溃，其中36次是唯一的。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t012bf3b289053e8263.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01c8b1b80895d49f5c.png)

许多崩溃由于是零除零指针和空指针解除引用。此外还发现了一些基于堆的越界写入，这些写入无法可靠地复现。

最后我们向VLC的安全团队披露了以下五个漏洞。

### <a class="reference-link" name="1.mkv::mkv_track_t::~mkv_track_t()%E7%9A%84Double%20Free%E6%BC%8F%E6%B4%9E"></a>1.mkv::mkv_track_t::~mkv_track_t()的Double Free漏洞

```
==79009==ERROR: AddressSanitizer: attempting double-free on 0x602000048e50 in thread T5:
mkv demux error: Couldn't allocate buffer to inflate data, ignore track 4
[000061100006a080] mkv demux error: Couldn't handle the track 4 compression
#0 0x4ac420 in __interceptor_free /home/symeon/Desktop/llvm-project/compiler-rt/lib/asan/asan_malloc_linux.cc:123:3
#1 0x7fb7722c3b6f in mkv::mkv_track_t::~mkv_track_t() /home/symeon/Desktop/vlc/modules/demux/mkv/mkv.cpp:895:5
#2 0x7fb77214ad4b in mkv::matroska_segment_c::ParseTrackEntry(libmatroska::KaxTrackEntry const*) /home/symeon/Desktop/vlc/modules/demux/mkv/matroska_segment_parse.cpp:992:13
```

上述漏洞在VLC 3.0.7版本中的以下提交当中被修复([http://git.videolan.org/?p=vlc.git;a=commit;h=81023659c7de5ac2637b4a879195efef50846102](http://git.videolan.org/?p=vlc.git;a=commit;h=81023659c7de5ac2637b4a879195efef50846102))

### <a class="reference-link" name="2.%20%E9%87%8A%E6%94%BE%E6%9C%AA%E5%9C%A8es_format_Clean%E4%B8%AD%E8%BF%9B%E8%A1%8Cmalloced%E7%9A%84%E5%9C%B0%E5%9D%80"></a>2. 释放未在es_format_Clean中进行malloced的地址

```
[000061100005ff40] mkv demux error: cannot load some cues/chapters/tags etc. (broken seekhead or file)
[000061100005ff40] =================================================================
==92463==ERROR: AddressSanitizer: attempting free on address which was not malloc()-ed: 0x02d000000000 in thread T5
mkv demux error: cannot use the segment
#0 0x4ac420 in __interceptor_free /home/symeon/Desktop/llvm-project/compiler-rt/lib/asan/asan_malloc_linux.cc:123:3
#1 0x7f7470232230 in es_format_Clean /home/symeon/Desktop/vlc/src/misc/es_format.c:496:9
#2 0x7f7452f82a6c in mkv::mkv_track_t::~mkv_track_t() /home/symeon/Desktop/vlc/modules/demux/mkv/mkv.cpp:892:5
#3 0x7f7452dd78e4 in std::default_delete&lt;mkv::mkv_track_t&gt;::operator()(mkv::mkv_track_t*) const /usr/lib/gcc/x86_64-linux-gnu/8/../../../../include/c++/8/bits/unique_ptr.h:81:2
```

### <a class="reference-link" name="3.mkv::demux_sys_t::FreeUnused()%E4%B8%AD%E7%9A%84%E5%A0%86%E6%BA%A2%E5%87%BA%E8%AF%BB%E5%8F%96"></a>3.mkv::demux_sys_t::FreeUnused()中的堆溢出读取

```
libva error: va_getDriverName() failed with unknown libva error,driver_name=(null)
[00006060001d1860] decdev_vaapi_drm generic error: vaInitialize: unknown libva error
[h264 @ 0x6190000a4680] top block unavailable for requested intra mode -1
[h264 @ 0x6190000a4680] error while decoding MB 10 0, bytestream 71
=================================================================
==104180==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x62500082c24f at pc 0x0000004ab6da bp 0x7f6f5ac3faf0 sp 0x7f6f5ac3f2a0
READ of size 128 at 0x62500082c24f thread T8
#0 0x4ab6d9 in __asan_memcpy /home/symeon/Desktop/llvm-project/compiler-rt/lib/asan/asan_interceptors_memintrinsics.cc:22:3
#1 0x7f6f5ad1748f in lavc_CopyPicture /home/symeon/Desktop/vlc/modules/codec/avcodec/video.c:435:13
#2 0x7f6f5ad13b89 in DecodeBlock /home/symeon/Desktop/vlc/modules/codec/avcodec/video.c:1259:17
#3 0x7f6f5ad0e537 in DecodeVideo /home/symeon/Desktop/vlc/modules/codec/avcodec/video.c:1356:12
```

### <a class="reference-link" name="4.%20mkv::demux_sys_t::FreeUnused()%E4%B8%AD%E7%9A%84%E5%A0%86%E6%BA%A2%E5%87%BA%E8%AF%BB%E5%8F%96"></a>4. mkv::demux_sys_t::FreeUnused()中的堆溢出读取

```
[0000611000069f40] mkv demux error: No tracks supported
=================================================================
==81972==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x6020000482c0 at pc 0x7f0a692c7a37 bp 0x7f0a6bf2ac10 sp 0x7f0a6bf2ac08
READ of size 8 at 0x6020000482c0 thread T7
#0 0x7f0a692c7a36 in mkv::demux_sys_t::FreeUnused() /home/symeon/Desktop/vlc/modules/demux/mkv/demux.cpp:267:34
#1 0x7f0a6937eaf1 in mkv::Open(vlc_object_t*) /home/symeon/Desktop/vlc/modules/demux/mkv/mkv.cpp:257:12
#2 0x7f0a86792691 in demux_Probe /home/symeon/Desktop/vlc/src/input/demux.c:180:15
#3 0x7f0a866d8d17 in module_load /home/symeon/Desktop/vlc/src/modules/modules.c:122:15
```

### <a class="reference-link" name="5.%20mkv::matroska_segment_c::TrackInit%E4%B8%AD%E7%9A%84%E5%A0%86%E6%BA%A2%E5%87%BA%E8%AF%BB%E5%8F%96"></a>5. mkv::matroska_segment_c::TrackInit中的堆溢出读取

```
=================================================================
==83326==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x6040000b3134 at pc 0x0000004ab6da bp 0x7ffb4f076250 sp 0x7ffb4f075a00
READ of size 13104 at 0x6040000b3134 thread T7
#0 0x4ab6d9 in __asan_memcpy /home/symeon/Desktop/llvm-project/compiler-rt/lib/asan/asan_interceptors_memintrinsics.cc:22:3
#1 0x7ffb4d84008d in mkv::matroska_segment_c::TrackInit(mkv::mkv_track_t*)::TrackCodecHandlers::StringProcessor_1783_handler(char const*&amp;, mkv::matroska_segment_c::TrackInit(mkv::mkv_track_t*)::HandlerPayload&amp;) /home/symeon/Desktop/vlc/modules/demux/mkv/matroska_segment_parse.cpp:1807:25
#2 0x7ffb4d83f6ab in mkv::matroska_segment_c::TrackInit(mkv::mkv_track_t*)::TrackCodecHandlers::StringProcessor_1783_callback(char const*, void*) /home/symeon/Desktop/vlc/modules/demux/mkv/matroska_segment_parse.cpp:1783:9
#3 0x7ffb4d7dc486 in (anonymous namespace)::StringDispatcher::send(char const* const&amp;, void* const&amp;) const /home/symeon/Desktop/vlc/modules/demux/mkv/string_dispatcher.hpp:128:13
```



## 11.其他模糊测试方法：使用libFuzz进行高级模糊测试

在搜索以前的技术时，我偶然发现了这篇博文，其中一位VLC开发人员使用libFuzz来获得更深入的覆盖。开发人员使用例如vlc_stream_MemoryNew()(https://www.videolan.org/developers/vlc/doc/doxygen/html/stream__memory_8c.html)，它从字节流中读取数据并对demux进程进行模糊处理。这说明了你在编写自己的测试代码和研究你的目标时越努力，将获得越好的结果。



## 12.有没有办法扫描/检查格式错误的MKV或AVI文件？

因为花费时间太长，所以我们没有从该角度进行研究。考虑到时间和精力的问题，我们没有将崩溃变成一个完全可用的漏洞。最好的防御措施是更新VLC并使用最新版本。如果有人利用这些崩溃创造恶意文件，反病毒软件将对这些文件进行文件签名检测并开始分析它。



## 13.总结

在最开始，我们对VLC的工作原理一无所知，然后我们学会了如何基于文档创建一个非常简单的检测小脚本。

之后，我们使用honggfuzz检测VLC，虽然在检测二进制文件的标准过程honggfuzz无法发挥作用，但我们通过调整一些参数可以成功检测二进制文件。

我们继续收集样本，编译和链接VLC与libhfuzz库添加覆盖支持，进行模糊测试，获取崩溃信息并对我们的崩溃进行分类！

然后，我们能够测量我们的初始覆盖率并改进我们的样本，从而提高整体覆盖率。仅针对.mkv格式，我们看到我们能够获得mkv文件格式的总共50％的覆盖率。请记住，VLC支持许多不同的视频和音频文件格式，因此还有很多可以模糊的代码！

最后，虽然我们在这个项目中使用了一个相对较快的虚拟机，但应该注意的是，即使是一个速度较慢的4GB虚拟机也可以使用并让你发现其中的漏洞。

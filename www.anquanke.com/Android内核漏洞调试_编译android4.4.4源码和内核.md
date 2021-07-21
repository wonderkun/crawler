> 原文链接: https://www.anquanke.com//post/id/105994 


# Android内核漏洞调试：编译android4.4.4源码和内核


                                阅读量   
                                **141301**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t019196071e23229ab9.jpg)](https://p4.ssl.qhimg.com/t019196071e23229ab9.jpg)

## 前言

android kernel漏洞进行源码调试需要编译aosp源码和内核，本文就其详细过程进行了图文讲解。

## 准备工作

一些碎碎念……本来因为想在mac上编译的，还专门买了一个外置的移动硬盘，然后自己按照官网和搜到的无数篇博客精心研究了很久很久，耗时三天，还是GG，但是基本上…xcode是个大坑，算了算了……反正最后始终没弄好，然后，虚拟机走起吧……

首先，虚拟机用的是mac上的parallels desktop，然后镜像是[Ubuntu 12.04.5 Desktop (64-bit)](http://releases.ubuntu.com/12.04/ubuntu-12.04.5-desktop-amd64.iso.torrent?_ga=2.244298688.451892976.1519576871-1559322823.1519576871)

然后android源码在[这里](https://pan.baidu.com/s/1ngsZs#list/path=%2FAndroid%E6%BA%90%E7%A0%81)下载，我没有用repo，直接从百度云取的，用的是android4.4.4_r1<br>[![](https://p1.ssl.qhimg.com/t018dcf8cb84b5b5351.png)](https://p1.ssl.qhimg.com/t018dcf8cb84b5b5351.png)<br>
这样一共只需要下载2G多点……而不是70G（死目

mac上虚拟机快速配置就可以快速安装好系统，不过**记得安装好后，修改一下硬件，空间给128G，内存改4096M，核数改2-4随便**。

## 安装Java JDK 1.6

jdk版本：jdk-6u45-linux-x64.bin<br>
下载地址：[http://app.nidc.kr/java/jdk-6u45-linux-x64.bin](http://app.nidc.kr/java/jdk-6u45-linux-x64.bin)

我们先在 /usr/local/目录下创建java文件夹：

```
cd /usr/local
sudo mkdir java
sudo cp [jdk-6u45-linux-x64.bin路径]  /usr/local/java
sudo chmod 777 jdk-6u45-linux-x64.bin
sudo ./jdk-6u45-linux-x64.bin
```

安装成功后,java文件夹下多了一个文件夹：jdk1.6.0_45/<br>
然后配置环境变量，用vim打开/ect/profile 文件,嗯，我不会用gedit，日常vim，这个其实随意。

```
sudo vim /etc/profile
```

添加下面的环境变量，要根据安装目录修改，并保存

```
# Java Environment
export JAVA_HOME=/usr/local/java/jdk1.6.0_45  

export JRE_HOME=/usr/local/java/jdk1.6.0_45/jre  

export CLASSPATH=.:$JAVA_HOME/lib:$JRE_HOME/lib:$CLASSPATH  

export PATH=$JAVA_HOME/bin:$JRE_HOME/bin:$JAVA_HOME:$PATH
```

重启后使其生效并进行验证<br>
也可使用下面的命令不重启使其生效，不过只针对当前域有效。

```
source /etc/profile
```

其实我是没重启的，直接source就行了，只要不另在终端里开标签或者重启终端就可以。<br>
输入java -version 进行验证安装,成功后返回如下

```
java version "1.6.0_45"
Java(TM) SE Runtime Environment (build 1.6.0_45-b06)
Java HotSpot(TM) 64-Bit Server VM (build 20.45-b01, mixed mode)
```

## 安装依赖

```
sudo apt-get install git gnupg flex bison gperf build-essential 
  zip curl libc6-dev libncurses5-dev:i386 x11proto-core-dev 
  libx11-dev:i386 libreadline6-dev:i386 libgl1-mesa-glx:i386 
  libgl1-mesa-dev g++-multilib mingw32 tofrodos 
  python-markdown libxml2-utils xsltproc zlib1g-dev:i386

sudo ln -s /usr/lib/i386-linux-gnu/mesa/libGL.so.1 /usr/lib/i386-linux-gnu/libGL.so
```

必须提到的是！我之前一直遇到很坑的问题，那就是虚拟机重启后打不开，始终没有解决，直到我不死心的尝试第n次，然后搜到了这个。<br>[http://www.cnblogs.com/wangzehuaw/p/4057604.html](http://www.cnblogs.com/wangzehuaw/p/4057604.html)<br>**划重点**

```
$ sudo apt-get install git gnupg flex bison gperf build-essential 
&gt;   zip curl libc6-dev libncurses5-dev:i386 x11proto-core-dev 
&gt;   libx11-dev:i386 libreadline6-dev:i386 libgl1-mesa-glx:i386 
&gt;   libgl1-mesa-dev g++-multilib mingw32 tofrodos 
&gt;   python-markdown libxml2-utils xsltproc zlib1g-dev:i386
Reading package lists... Done
Building dependency tree       
Reading state information... Done
zip is already the newest version.
zip set to manually installed.
gnupg is already the newest version.
Some packages could not be installed. This may mean that you have
requested an impossible situation or if you are using the unstable
distribution that some required packages have not yet been created
or been moved out of Incoming.
The following information may help to resolve the situation:

The following packages have unmet dependencies:
 libgl1-mesa-glx:i386 : Depends: libglapi-mesa:i386 (= 8.0.4-0ubuntu0.6)
                        Recommends: libgl1-mesa-dri:i386 (&gt;= 7.2)
E: Unable to correct problems, you have held broken packages.
```

<strong>提示信息说缺少依赖库无法安装libgl1-mesa-glx:i386，那么就不要安装这个库了，从上面的install列表中减去这个库。<br>
libgl1-mesa-glx:i386。如果强制安装了这个库会导致重启或关机后无法进入ubuntu问题，很严重。<br>
如果也遇到了无法进入ubuntu系统的问题，请重装系统时不要安装这个库。</strong><br>
我真的第一次见到会break desktop的库……服了服了。

**就因为这个坑了我三天！！！**

所以像我一样直接去掉吧。

```
sudo apt-get install git gnupg flex bison gperf build-essential zip curl libc6-dev libncurses5-dev:i386 x11proto-core-dev libx11-dev:i386 libreadline6-dev:i386 libgl1-mesa-dev g++-multilib mingw32 tofrodos python-markdown libxml2-utils xsltproc zlib1g-dev:i386
sudo ln -s /usr/lib/i386-linux-gnu/mesa/libGL.so.1 /usr/lib/i386-linux-gnu/libGL.so
```

## 解压源码

把之前下载的源码的7z包解压，比如我是建了个目录aosp，然后解压后，就有个android-4.4.4_r1的文件夹。<br>[![](https://p2.ssl.qhimg.com/t01ef463b4ea19d620b.png)](https://p2.ssl.qhimg.com/t01ef463b4ea19d620b.png)

7z文件需要下一个东西来解压

```
sudo apt-get install p7zip-full
7z x android-4.4.4_r1.7z
```

解压好之后，进入源码路径，如果你的目录结构和我一样，就是

```
cd ~/aosp/android-4.4.4_r1
```

## 编译源码

### <a class="reference-link" name="%E6%B8%85%E7%90%86"></a>清理

命令删除所有以前编译操作的已有输出：

```
make clobber
```

### <a class="reference-link" name="%E8%AE%BE%E7%BD%AE%E7%8E%AF%E5%A2%83"></a>设置环境

使用build目录中的envsetup.sh脚本初始化环境

```
source build/envsetup.sh
```

### <a class="reference-link" name="%E9%80%89%E6%8B%A9%E7%9B%AE%E6%A0%87"></a>选择目标

因为我不下载到实体机里，就直接输入lunch，然后回车即可。<br>
默认选择第一个，即lunch aosp_arm-eng，该命令表示针对模拟器进行完整编译，并且所有调试功能均处于启用状态。

### <a class="reference-link" name="%E8%BF%9B%E8%A1%8C%E7%BC%96%E8%AF%91"></a>进行编译

编译前先看看你配置了几个核，然后make -j(核数✖2)

```
cat /proc/cpuinfo | grep processor
```

[![](https://p5.ssl.qhimg.com/t01bde9f3d87757c098.png)](https://p5.ssl.qhimg.com/t01bde9f3d87757c098.png)<br>
可看到自己创建的虚拟机CPU核心共有2个，所以make -j4<br>
编译后输出的文件都放在了源码根目录下的out文件中。

## 启动模拟器

```
emulator -partition-size 300
```

[![](https://p0.ssl.qhimg.com/t013d2b5b2d42861630.png)](https://p0.ssl.qhimg.com/t013d2b5b2d42861630.png)

## 导入android源码进android studio

网上的做法比较乱，我只写一下我是怎么做的。<br>
1.在整个Android源码全编成功之后，然后编译idegen模块，用以生成Android studio的工程配置文件,编译成功之后就生成了idegen.jar（out/host/darwin-x86/framework/idegen.jar），运行如下命令：

```
source build/ensetup.sh
mmm development/tools/idegen/
```

[![](https://p1.ssl.qhimg.com/t01b93a78c4fa68dbde.png)](https://p1.ssl.qhimg.com/t01b93a78c4fa68dbde.png)<br>
2.在源码根目录生成对应的android.ipr、android.iml IEDA工程配置文件。以便于AndroidStudio可以打开项目

```
development/tools/idegen/idegen.sh
```

[![](https://p3.ssl.qhimg.com/t01179534f6a0907ef3.png)](https://p3.ssl.qhimg.com/t01179534f6a0907ef3.png)<br>
3.下载android studio并启动<br>[![](https://p1.ssl.qhimg.com/t01ff59e2ce1d4940be.png)](https://p1.ssl.qhimg.com/t01ff59e2ce1d4940be.png)

```
cd ~/android-studio/bin
./studio.sh
```

第一次启动要安装sdk，所以记得翻墙。<br>[![](https://p1.ssl.qhimg.com/t01331d651e05745016.png)](https://p1.ssl.qhimg.com/t01331d651e05745016.png)<br>
4.导入<br>
打开 Android studio，选择刚刚生成的 android.ipr 打开，等待加载好了就可以了。<br>[![](https://p0.ssl.qhimg.com/t01be23f760a5255912.png)](https://p0.ssl.qhimg.com/t01be23f760a5255912.png)

## 下载源代码

[https://source.android.com/source/building-kernels](https://source.android.com/source/building-kernels)<br>
承接之前编译的android4.4.4的系统源码，所以说是模拟平台，用goldfish

```
sakura@ubuntu:~$ git clone https://aosp.tuna.tsinghua.edu.cn/kernel/goldfish
```

## 查看各种版本的goldfish

```
sakura@ubuntu:~$ cd goldfish/
sakura@ubuntu:~/goldfish$ git branch -a
* master
  remotes/origin/HEAD -&gt; origin/master
  remotes/origin/android-3.10
  remotes/origin/android-3.18
  remotes/origin/android-3.4
  remotes/origin/android-goldfish-2.6.29
  remotes/origin/android-goldfish-3.10
  remotes/origin/android-goldfish-3.10-k-dev
  remotes/origin/android-goldfish-3.10-l-mr1-dev
  remotes/origin/android-goldfish-3.10-m-dev
  remotes/origin/android-goldfish-3.10-n-dev
  remotes/origin/android-goldfish-3.18
  remotes/origin/android-goldfish-3.18-dev
  remotes/origin/android-goldfish-3.4
  remotes/origin/android-goldfish-3.4-l-mr1-dev
  remotes/origin/android-goldfish-4.4-dev
  remotes/origin/heads/for/android-goldfish-3.18-dev
  remotes/origin/linux-goldfish-3.0-wip
  remotes/origin/master
sakura@ubuntu:~/goldfish$
```

我们选择3.4版本

## 切换分支

```
sakura@ubuntu:~/goldfish$ git checkout remotes/origin/android-goldfish-3.4 -b goldfish3.4
Checking out files: 100% (38854/38854), done.
Branch goldfish3.4 set up to track remote branch android-3.4 from origin.
Switched to a new branch 'goldfish3.4'
```

## 配置交叉编译链

首先，要翻墙,mac及其虚拟机可以参考[我的博客](http://eternalsakura13.com/2018/02/02/proxy/)<br>
然后获取交叉编译链

```
sakura@ubuntu:~$ git clone https://android.googlesource.com/platform/prebuilts/gcc/linux-x86/arm/arm-eabi-4.6
```

设置环境变量

```
sakura@ubuntu:~$ sudo vim /etc/profile
```

在打开的文件最末添加

```
export PATH=/home/sakura/arm-eabi-4.6/bin:$PATH
```

然后使配置生效

```
sakura@ubuntu:~$ source /etc/profile
```

确认一下

```
sakura@ubuntu:~$ echo $PATH
/home/sakura/arm-eabi-4.6/bin:/home/sakura/Android/Sdk/platform-tools:/usr/local/java/jdk1.6.0_45/bin:/usr/local/java/jdk1.6.0_45/jre/bin:/usr/local/java/jdk1.6.0_45:/home/sakura/Android/Sdk/platform-tools:/usr/local/java/jdk1.6.0_45/bin:/usr/local/java/jdk1.6.0_45/jre/bin:/usr/local/java/jdk1.6.0_45:/usr/lib/lightdm/lightdm:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games
```

## 配置编译选项，进行编译

```
sakura@ubuntu:~/goldfish$ export ARCH=arm
sakura@ubuntu:~/goldfish$ export CROSS_COMPILE=arm-eabi-
sakura@ubuntu:~/goldfish$ export SUBARCH=arm
sakura@ubuntu:~/goldfish$ make goldfish_armv7_defconfig
  HOSTCC  scripts/basic/fixdep
  HOSTCC  scripts/kconfig/conf.o
  SHIPPED scripts/kconfig/zconf.tab.c
  SHIPPED scripts/kconfig/zconf.lex.c
  SHIPPED scripts/kconfig/zconf.hash.c
  HOSTCC  scripts/kconfig/zconf.tab.o
  HOSTLD  scripts/kconfig/conf
#
# configuration written to .config
#
```

增加内核编译选项,修改goldfish/.config配置文件

```
sakura@ubuntu:~/goldfish$ vim /home/sakura/goldfish/.config
```

添加以下两行

```
CONFIG_DEBUG_INFO=y #显示vmlinux符号
CONFIG_KGDB=y #开启kgdb
```

执行 make 命令进行编译

```
sakura@ubuntu:~/goldfish$ make
```

## 启动

编译成功后会显示<br>[![](https://p2.ssl.qhimg.com/t01bdcfbd005166ff5b.png)](https://p2.ssl.qhimg.com/t01bdcfbd005166ff5b.png)

```
OBJCOPY arch/arm/boot/Image
  Kernel: arch/arm/boot/Image is ready
  AS      arch/arm/boot/compressed/head.o
  GZIP    arch/arm/boot/compressed/piggy.gzip
  AS      arch/arm/boot/compressed/piggy.gzip.o
  CC      arch/arm/boot/compressed/misc.o
  CC      arch/arm/boot/compressed/decompress.o
  CC      arch/arm/boot/compressed/string.o
  SHIPPED arch/arm/boot/compressed/lib1funcs.S
  AS      arch/arm/boot/compressed/lib1funcs.o
  SHIPPED arch/arm/boot/compressed/ashldi3.S
  AS      arch/arm/boot/compressed/ashldi3.o
  LD      arch/arm/boot/compressed/vmlinux
  OBJCOPY arch/arm/boot/zImage
  Kernel: arch/arm/boot/zImage is ready
```

以指定的内核启动模拟器

```
emulator -verbose -show-kernel -kernel ~/goldfish/arch/arm/boot/zImage
```

## 错误处理

输入emulator的时候报错

```
No command 'emulator' found, did you mean:
 Command 'qemulator' from package 'qemulator' (universe)
emulator: command not found
```

我至今不知道为什么经常emulator就没了。。但是只要输入lunch,然后再make一下，几分钟就好了……

## 参考链接

[https://source.android.com/source/initializing#installing-required-packages-ubuntu-1204](https://source.android.com/source/initializing#installing-required-packages-ubuntu-1204)<br>[https://source.android.com/source/requirements#older-versions](https://source.android.com/source/requirements#older-versions)<br>[https://bbs.pediy.com/thread-218366.htm](https://bbs.pediy.com/thread-218366.htm)<br>[https://bbs.pediy.com/thread-218513.htm](https://bbs.pediy.com/thread-218513.htm)

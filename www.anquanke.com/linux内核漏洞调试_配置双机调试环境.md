> 原文链接: https://www.anquanke.com//post/id/105342 


# linux内核漏洞调试：配置双机调试环境


                                阅读量   
                                **165138**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t01da57829a99697f21.jpg)](https://p3.ssl.qhimg.com/t01da57829a99697f21.jpg)



## 选择kernel的版本

搜索含有dbgsym的内核版本<br>`apt-cache search linux-image | grep dbgsym | grep 4.11`<br>
搜索特定source code的内核版本<br>`apt-cache search linux-source`<br>
然后选择一个



## 安装内核

搜索要下载的linux内核版本<br>`apt-cache search linux-image | grep linux-image | grep generic`<br>
安装内核<br>`sudo apt-get install linux-image-4.10.0-19-generic`<br>
查看安装的内核版本<br>`sudo dpkg --list | grep linux-image`<br>
重启，在grub之前，按住shift，选择我们的内核<br>[![](https://p4.ssl.qhimg.com/t01a1494795ba2cf51c.png)](https://p4.ssl.qhimg.com/t01a1494795ba2cf51c.png)<br>[![](https://p2.ssl.qhimg.com/t0180f76dffb64af68a.png)](https://p2.ssl.qhimg.com/t0180f76dffb64af68a.png)

验证新内核启用<br>`uname -sr`



## 安装符号文件

在终端输入下面的代码

```
codename=$(lsb_release -c | awk  '`{`print $2`}`')
sudo tee /etc/apt/sources.list.d/ddebs.list &lt;&lt; EOF
deb http://ddebs.ubuntu.com/ $`{`codename`}`      main restricted universe multiverse
deb http://ddebs.ubuntu.com/ $`{`codename`}`-security main restricted universe multiverse
deb http://ddebs.ubuntu.com/ $`{`codename`}`-updates  main restricted universe multiverse
deb http://ddebs.ubuntu.com/ $`{`codename`}`-proposed main restricted universe multiverse
EOF
```

添加访问符号服务器的密钥文件：<br>`wget -O - http://ddebs.ubuntu.com/dbgsym-release-key.asc | sudo apt-key add -`<br>
执行`sudo apt-get update`更新<br>
执行如下命令开始下载符号包：

```
sudo apt-get install linux-image-`uname -r`-dbgsym
```



## 安装kernel对应的源代码

打开/etc/apt/sources.list，启用deb-src，sudo apt-get update更新

```
vim /etc/apt/sources.list
去掉下面这句话的注释
deb-src http://us.archive.ubuntu.com/ubuntu/ xenial main restricted

...
sudo apt-get update
```
<li>搜索所有版本的source code:`apt-cache search linux-source`
</li>
<li>安装指定版本的source code:`sudo apt-get install linux-source-4.10.0`
</li>
下载好的源码会被放在/usr/src目录下。<br>[![](https://p2.ssl.qhimg.com/t0181b1af87c39a2146.png)](https://p2.ssl.qhimg.com/t0181b1af87c39a2146.png)<br>[![](https://p2.ssl.qhimg.com/t01ec8a8a5085417a12.png)](https://p2.ssl.qhimg.com/t01ec8a8a5085417a12.png)

解压缩得到源码<br>`sudo tar -xvf linux-source-4.10.0.tar.bz2`

一切都安装好了之后，就可以拷贝一份我们的虚拟机，一个作为host,一个作为target



## 移除打印机，添加串口

打印机会占用我们的串口

### <a class="reference-link" name="target"></a>target

[![](https://p5.ssl.qhimg.com/t01d03c0a5e59d4ee2b.png)](https://p5.ssl.qhimg.com/t01d03c0a5e59d4ee2b.png)

### <a class="reference-link" name="host"></a>host

[![](https://p0.ssl.qhimg.com/t01eb7ad9a5d96cdc33.jpg)](https://p0.ssl.qhimg.com/t01eb7ad9a5d96cdc33.jpg)



## 配置target

需要让target在开机时候进入kgdb的调试状态，首先需要修改grub文件，增加grub引导时候的菜单项。

`sudo vim /etc/grub.d/40_custom`<br>
修改的内容从/boot/grub/grub.cfg里复制，复制一个菜单项（menuentry）过来，再把菜单名中增加调试信息，然后在内核命令行中增加KGDB选项，即下面这样：<br>**新增部分：kgdbwait kgdb8250=io,03f8,ttyS0,115200,4 kgdboc=ttyS0,115200 kgdbcon nokaslr**

```
#!/bin/sh
exec tail -n +3 $0
# This file provides an easy way to add custom menu entries.  Simply type the
# menu entries you want to add after this comment.  Be careful not to change
# the 'exec tail' line above.
menuentry 'Ubuntu,KGDB with nokaslr' --class ubuntu --class gnu-linux --class gnu --class os $menuentry_id_option 'gnulinux-4.10.0-19-generic-advanced-32ee8e9c-31e6-494c-a9ea-1a416cbfeca7' `{`
                recordfail
                load_video
                gfxmode $linux_gfx_mode
                insmod gzio
                if [ x$grub_platform = xxen ]; then insmod xzio; insmod lzopio; fi
                insmod part_msdos
                insmod ext2
                set root='hd0,msdos1'
                if [ x$feature_platform_search_hint = xy ]; then
                  search --no-floppy --fs-uuid --set=root --hint-bios=hd0,msdos1 --hint-efi=hd0,msdos1 --hint-baremetal=ahci0,msdos1  32ee8e9c-31e6-494c-a9ea-1a416cbfeca7
                else
                  search --no-floppy --fs-uuid --set=root 32ee8e9c-31e6-494c-a9ea-1a416cbfeca7
                fi
                echo    'Ubuntu,KGDB with nokaslr ...'
                linux   /boot/vmlinuz-4.10.0-19-generic root=UUID=32ee8e9c-31e6-494c-a9ea-1a416cbfeca7 ro find_preseed=/preseed.cfg auto noprompt priority=critical locale=en_US quiet kgdbwait kgdb8250=io,03f8,ttyS0,115200,4 kgdboc=ttyS0,115200 kgdbcon nokaslr
                echo    'Loading initial ramdisk ...'
                initrd  /boot/initrd.img-4.10.0-19-generic
        `}`
```

修改grub的配置后，需要执行sudo update-grub来更新。更新后目标机器就准备好了。<br>
重启按住shift,进入刚才添加的menu即可进入到被调试状态。



## 配置host

设置串口通信的波特率<br>`sudo stty -F /dev/ttyS0 115200`<br>
要查看是否设置成功<br>`sudo stty -F /dev/ttyS0`<br>
注意这个每次host重启都要再输入一遍，嗯，写个shell吧。



## 调试

编写config，用source加载（直接在gdb里输入也可）

```
set architecture i386:x86-64:intel
target remote /dev/ttyS0
```

使用gdb来调试带符号的vmlinux

```
gdb -s /usr/lib/debug/boot/vmlinux-4.10.0-19-generic
gdb &gt; source config
```

符号加载完成，bt查看当前栈帧，c运行内核。<br>[![](https://p3.ssl.qhimg.com/t01c325ce6aae62dfde.jpg)](https://p3.ssl.qhimg.com/t01c325ce6aae62dfde.jpg)<br>[![](https://p1.ssl.qhimg.com/t01c6a70c78d1d9fafa.png)](https://p1.ssl.qhimg.com/t01c6a70c78d1d9fafa.png)<br>[![](https://p1.ssl.qhimg.com/t01dbe548eda795d6ae.png)](https://p1.ssl.qhimg.com/t01dbe548eda795d6ae.png)



## 查看源码遇到的问题

[![](https://p2.ssl.qhimg.com/t01d7d4dd0e5c37d559.png)](https://p2.ssl.qhimg.com/t01d7d4dd0e5c37d559.png)

可以看到，list本来应该显示具体的源码，但是这里只是打印出了它所在的文件，这是因为在这个路径下没有源码。<br>
所以说我们就建立这个路径，然后把源码放进去

[![](https://p3.ssl.qhimg.com/t0114168c1e0fa48889.png)](https://p3.ssl.qhimg.com/t0114168c1e0fa48889.png)<br>
然后dir设置好目录<br>`dir /build/linux-hwe-edge-gyUj63/linux-hwe-edge-4.10.0`<br>
现在就可以查看源码了。<br>[![](https://p0.ssl.qhimg.com/t0101aa727ef02cbb8a.png)](https://p0.ssl.qhimg.com/t0101aa727ef02cbb8a.png)



## 单步调试

我从头开始说：
<li>host<br>
target remote /dev/ttyS0<br>
按c继续运行target</li>
<li>target<br>
一开始停在下图这个地方，host按c之后，target继续运行进入系统<br>[![](https://p3.ssl.qhimg.com/t01c6a70c78d1d9fafa.png)](https://p3.ssl.qhimg.com/t01c6a70c78d1d9fafa.png)<br>
然后输入`sudo su &amp;&amp; echo g &gt; "/proc/sysrq-trigger"`<br>[![](https://p4.ssl.qhimg.com/t01158ea30fa6aa3695.png)](https://p4.ssl.qhimg.com/t01158ea30fa6aa3695.png)<br>
这时候target应该进入假死状态，其实就是完全动不了。<br>
这一步就是打开target的kgdb调试。</li>
<li>host<br>
这时候host那里不再是<br>[![](https://p2.ssl.qhimg.com/t01a428669d33f6f514.png)](https://p2.ssl.qhimg.com/t01a428669d33f6f514.png)<br>
而是停下来了，可以下断了<br>[![](https://p3.ssl.qhimg.com/t018b60f35e0e32f028.jpg)](https://p3.ssl.qhimg.com/t018b60f35e0e32f028.jpg)<br>
在你想要调试的函数下断点，然后按c，恢复target执行。</li>
<li>target<br>
这样就可以运行我们的poc了<br>[![](https://p2.ssl.qhimg.com/t01d611d001bd26f1d4.jpg)](https://p2.ssl.qhimg.com/t01d611d001bd26f1d4.jpg)
</li>
<li>host<br>
回到host，此时应该已经停在断点了，然后按n可以单步调试。<br>[![](https://p5.ssl.qhimg.com/t017f0df062ed4f179f.jpg)](https://p5.ssl.qhimg.com/t017f0df062ed4f179f.jpg)<br>[![](https://p1.ssl.qhimg.com/t01db6940243b005c03.jpg)](https://p1.ssl.qhimg.com/t01db6940243b005c03.jpg)
</li>
至此，内核调试的整个配置和调试方法都写完了。



## 参考链接

[ubuntu内核调试要点](http://advdbg.org/blogs/advdbg_system/search.aspx?q=%E5%86%85%E6%A0%B8%E8%B0%83%E8%AF%95&amp;p=1)



## 其他

内核调试的坑实在太深，一开始参考了muhe师傅的文章用gdb+qemu调，然后编译了kernel 4.x之后，编译不报错，但是调试过程简直了，gdb花式挂不上去，看网上说某些版本要改gdb源码重新编译gdb……放弃了放弃了。<br>
感谢教我搭建双机调试的师傅……<br>
内核还是很容易调飞的，有时候花式加载不出来。

另外如果下载符号文件太慢，可以参考我的这篇文章，在虚拟机里用ss代理。<br>[http://eternalsakura13.com/2018/02/02/proxy/](http://eternalsakura13.com/2018/02/02/proxy/)

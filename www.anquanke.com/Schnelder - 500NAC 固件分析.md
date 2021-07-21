> 原文链接: https://www.anquanke.com//post/id/214730 


# Schnelder - 500NAC 固件分析


                                阅读量   
                                **124496**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t01e0e84d25ef138319.jpg)](https://p5.ssl.qhimg.com/t01e0e84d25ef138319.jpg)



## 一、固件基本信息

<a name="2277-1578842637730"></a>设备简介：5500NAC 是一个自动化的逻辑控制器，主要应用在楼宇控制系统，配备WEB界面以<a name="8846-1578842709818"></a>及cubs/MODBUS/Bacnet通信协议

<a name="7789-1578842402161"></a>获取方式：固件可以通过官网直接下载，附件中也包含固件。

<a name="4258-1578842558210"></a>固件压缩包文件名：5500NAC_Firmware_V1.6.0.zip

<a name="8020-1578842565482"></a>固件大小：8402400 字节 (8205 KiB)

<a name="2959-1579180072320"></a>SHA256:  **81D2B46A6505B28D94DB9C7C9CF16EB38CC316747A1CCB93A3FBCE2C4487245E**

<a name="9456-1578842448931"></a>固件文件分析：解压后可获得 .img 系统镜像 binwalk 可直接解压出文件系统



## 二、固件分析

### <a name="7060-1578842845001"></a>1.固件文件系统分析

<a name="8828-1578842738435"></a>使用 binwalk 对其分析并尝试解压，获取文件系统

[![](https://p3.ssl.qhimg.com/t01003488ccd1d92733.png)](https://p3.ssl.qhimg.com/t01003488ccd1d92733.png)

[![](https://p3.ssl.qhimg.com/t01efb686217ecfc6f8.png)](https://p3.ssl.qhimg.com/t01efb686217ecfc6f8.png)

### <a name="5299-1578842738435"></a>2.敏感信息发现

<a name="7966-1578842869672"></a>查看 /etc 文件夹中各类配置文件，发现了多个服务的默认账户信息

[![](https://p1.ssl.qhimg.com/t01b42b4d0b7fa215a3.png)](https://p1.ssl.qhimg.com/t01b42b4d0b7fa215a3.png)

[![](https://p5.ssl.qhimg.com/t01cc0ddfc88364da55.png)](https://p5.ssl.qhimg.com/t01cc0ddfc88364da55.png)

[![](https://p1.ssl.qhimg.com/t0132991b0ada5f2da2.png)](https://p1.ssl.qhimg.com/t0132991b0ada5f2da2.png)<a name="1650-1578842738435"></a>

### <a name="2912-1578842768701"></a>3.业务代码解密&amp;审计

<a name="9241-1578842887961"></a>经分析，该固件业务功能采用Lua编写，查看/lib/ 文件夹发现大量.lua 文件

[![](https://p4.ssl.qhimg.com/t01dfeeaaa1f1a733e5.png)](https://p4.ssl.qhimg.com/t01dfeeaaa1f1a733e5.png)

<a name="5470-1578842768701"></a>打开某些文件，却发现是各种乱码，编辑器提示是编码问题，换了各种编码后发现并不能改变乱码现象

[![](https://p3.ssl.qhimg.com/t01caeb34e644ce32c6.png)](https://p3.ssl.qhimg.com/t01caeb34e644ce32c6.png)

<a name="3031-1578842768701"></a>随后想到，lua 存在各种加密和编译方式（但编译后后缀大都会发生改变如 luac），审计发现开头标志位 LJ 到网上各种搜资料，最终在看雪一篇文章中发现了蛛丝马迹

[![](https://p1.ssl.qhimg.com/t01e06bcd5ce9159253.png)](https://p1.ssl.qhimg.com/t01e06bcd5ce9159253.png)

[![](https://p2.ssl.qhimg.com/t01e897153625111dd3.png)](https://p2.ssl.qhimg.com/t01e897153625111dd3.png)

[![](https://p0.ssl.qhimg.com/t01d24f6cabbcb3c61f.png)](https://p0.ssl.qhimg.com/t01d24f6cabbcb3c61f.png)

[`{`传送门`}`](https://www.anquanke.com/post/id/90241)，在这里我重点演示一下，使用 ljd 直接反编译 luajit 伪码的流程。
<li style="list-style: none;">
<ul>
<li>
<a name="8615-1578842768701"></a>在不同的版本中，Opcode 的不同会导致解析结果的不同，所以要首先要确定固件中的lua文件是由哪个版本的luajit以及lua编译的（否则会出错）</li>
<li>
<a name="5957-1578842768701"></a>在 /usr/bin 中找到 luajit文件</li>
[![](https://p3.ssl.qhimg.com/t019d10e242e5d64454.png)](https://p3.ssl.qhimg.com/t019d10e242e5d64454.png)

<a name="7481-1578842768701"></a>使用ghidra反汇编 luajit 查找关键字符串 lua 确定了 luajit 以及 lua 的版本

[![](https://p1.ssl.qhimg.com/t011ee13fa7e6aa9794.png)](https://p1.ssl.qhimg.com/t011ee13fa7e6aa9794.png)

[![](https://p3.ssl.qhimg.com/t0138204e7f277be9c5.png)](https://p3.ssl.qhimg.com/t0138204e7f277be9c5.png)

<a name="3639-1578842768701"></a>从 luajit 官网下载相对应版本的demo 查看/src/lj_bc.h头文件中的opcode

[![](https://p1.ssl.qhimg.com/t011687a6035b7ff4ba.png)](https://p1.ssl.qhimg.com/t011687a6035b7ff4ba.png)

<a name="8998-1578842768701"></a>在 ljd 工具目录下 有两处代码引用了 Opcode 分别是 ljd/ljd/bytecode/instructions.py 和 ljd/ljd/rawdump/code/py

[![](https://p0.ssl.qhimg.com/t014d2ad6d6f730022c.png)](https://p0.ssl.qhimg.com/t014d2ad6d6f730022c.png)

[![](https://p1.ssl.qhimg.com/t011764a83be163c99b.png)](https://p1.ssl.qhimg.com/t011764a83be163c99b.png)

<a name="8646-1578842768701"></a>对比 lj_bc.h 中的 Opcode 定义一个一个改就可以了，ljd 默认是 2.1.0版本的，多的注释，少的加上。

<a name="4692-1578842768701"></a>由于我要反编译许多源码，所以临时改了一下 /ljd/main.py 使其可以支持多文件，并且将反编译出来的demo 写入新的文件demo如下（这里我反编译的目录是固件里的/lib目录）：****

```
import os
import re
import ljdmain
import sys def get_filelist(dir): ##获取包含绝对路径的文件列表 Filelist = []
for home, dirs, files in os.walk(path): for filename in files: #文件名列表， 包含完整路径 Filelist.append(os.path.join(home, filename)) return Filelist def mkdir(path): ##创建文件夹# 引入模块
import os# 去除首位空格 path = path.strip()# 去除尾部\ 符号path = path.rstrip("\\")# 判断路径是否存在# 存在 True# 不存在 False isExists = os.path.exists(path)# 判断结果
if not isExists: os.makedirs(path) print path + ' 创建成功'
return True
else :#如果目录存在则不创建， 并提示目录已存在 print path + ' 目录已存在'
return False# 调用函数if __name__ == "__main__": path = '/home/murkfox/ljd/lib'##
把固件中lib目录复制到了ljd工具目录下Filelist = get_filelist(path)## 获取被反编译的源码目录结构
for file in Filelist: ##创建空文件， 如果目录不存在就创建目录（ 将输出重定向至创建的空文件中） fil = file.split("/") fil[4] = "libdec"
ffi = ""
mkpath = ""
for i in range(len(fil)): if i &gt; 0: ffi = ffi + "/" + fil[i]
if i &lt; len(fil) - 1: mkpath = mkpath + "/" + fil[i]# mkpath = mkpath + "/"#
print(mkpath)# mkdir(mkpath) if re.search(r "\.lua", file): ##遍历要反编译的目录， 找到需要被反编译的文件 mkdir(mkpath) with open(ffi, "w") as fl: ##反编译文件， 并将反编译demo输出至对应文件
try: fl.write("## Dec file \n") sys.stdout = fl ljdmain.main(file) fl.close() except: pass
```

<a name="6334-1578842768701"></a>如下是被逆向出来的目录以及文件内容

[![](https://p0.ssl.qhimg.com/t014eef078c4796cdf7.png)](https://p0.ssl.qhimg.com/t014eef078c4796cdf7.png)

[![](https://p1.ssl.qhimg.com/t01e24b5683e0b300b4.png)](https://p1.ssl.qhimg.com/t01e24b5683e0b300b4.png)

<a name="4195-1578842768701"></a>很多从代码审计来看，程序多处操作都是直接通过系统命令完成操作测试文件上传处的命令执行成功

[![](https://p4.ssl.qhimg.com/t013331ba506ea53248.png)](https://p4.ssl.qhimg.com/t013331ba506ea53248.png)

[![](https://p1.ssl.qhimg.com/t017c5c59994ede34cc.png)](https://p1.ssl.qhimg.com/t017c5c59994ede34cc.png)<a name="5494-1597703342908"></a>

<a name="6160-1579098214620"></a>由于设备为linux系统，在ping 命令没有加 -c 导致ping 程序一直执行，引发了拒绝服务，设备直接下线。

<a name="2090-1579098218222"></a>也发现了许多有趣的地方

[![](https://p5.ssl.qhimg.com/t0133bad0da4ab51286.png)](https://p5.ssl.qhimg.com/t0133bad0da4ab51286.png)

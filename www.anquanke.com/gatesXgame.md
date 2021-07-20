> 原文链接: https://www.anquanke.com//post/id/226747 


# gatesXgame


                                阅读量   
                                **122564**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t01eff83d970fa92872.jpg)](https://p0.ssl.qhimg.com/t01eff83d970fa92872.jpg)



## 脱UPX壳

ida一打开发现是个标准的UPX的代码

[![](https://p3.ssl.qhimg.com/t01fa44fcdf5c33214f.png)](https://p3.ssl.qhimg.com/t01fa44fcdf5c33214f.png)

找到最后一个jmp跳过去即可

[![](https://p5.ssl.qhimg.com/t019c616cff3e536674.png)](https://p5.ssl.qhimg.com/t019c616cff3e536674.png)

后面修IAT啥的就不说了



## 去除花指令

首先进入start 然后找到main函数

[![](https://p4.ssl.qhimg.com/t011cc323e7f09d619d.png)](https://p4.ssl.qhimg.com/t011cc323e7f09d619d.png)

这个函数只是简单的判断了下是否是64位系统的环境，不是则直接退出

[![](https://p4.ssl.qhimg.com/t01936aa79e76df0ad4.png)](https://p4.ssl.qhimg.com/t01936aa79e76df0ad4.png)

可以看到通过jmp call ret 这样的指令把我们的IDA F5功能给搞了

[![](https://p2.ssl.qhimg.com/t0125c197d703c5b575.png)](https://p2.ssl.qhimg.com/t0125c197d703c5b575.png)

[![](https://p0.ssl.qhimg.com/t01baaaa27e9bd5f027.png)](https://p0.ssl.qhimg.com/t01baaaa27e9bd5f027.png)

往下面看又可以看出一种混淆

[![](https://p0.ssl.qhimg.com/t01ceca6abc6797ed8d.png)](https://p0.ssl.qhimg.com/t01ceca6abc6797ed8d.png)

使用OD插件来去除混淆<br>
添加模式

[![](https://p5.ssl.qhimg.com/t0155aa7fa3408e136c.png)](https://p5.ssl.qhimg.com/t0155aa7fa3408e136c.png)

[![](https://p5.ssl.qhimg.com/t01147b444b9e8d9e6f.png)](https://p5.ssl.qhimg.com/t01147b444b9e8d9e6f.png)

去除混淆后保存，这里就不细看了主要是比较了下输入是否是npointer`{`开头

[![](https://p2.ssl.qhimg.com/t01e598023909c49a3b.png)](https://p2.ssl.qhimg.com/t01e598023909c49a3b.png)

继续看这个函数申请了一块内存地址然后把参数一里面的东西拷贝过去了并且执行了，这个函数里面还有个check windbg的函数，感兴趣可以看看

[![](https://p4.ssl.qhimg.com/t010c99bc83837281af.png)](https://p4.ssl.qhimg.com/t010c99bc83837281af.png)



## 32切换64

首先断点下载到这里

[![](https://p5.ssl.qhimg.com/t01f168752328428300.png)](https://p5.ssl.qhimg.com/t01f168752328428300.png)

输入准备的key

[![](https://p2.ssl.qhimg.com/t019e7f9f2d0ffb4c38.png)](https://p2.ssl.qhimg.com/t019e7f9f2d0ffb4c38.png)

代码拷贝到0x4a0000里面了

[![](https://p2.ssl.qhimg.com/t0122df286d987a6adf.png)](https://p2.ssl.qhimg.com/t0122df286d987a6adf.png)

继续在这里下断点

[![](https://p5.ssl.qhimg.com/t014015b5ad8e8dd6aa.png)](https://p5.ssl.qhimg.com/t014015b5ad8e8dd6aa.png)

可以看出ebx是输入的长度 ecx现在要取的位置

[![](https://p0.ssl.qhimg.com/t01c93fbe279a114cd7.png)](https://p0.ssl.qhimg.com/t01c93fbe279a114cd7.png)

这两句执行完就是 push 0x33

[![](https://p5.ssl.qhimg.com/t01ca2448af08e3bad9.png)](https://p5.ssl.qhimg.com/t01ca2448af08e3bad9.png)

call这个地方就是一个混淆了

[![](https://p0.ssl.qhimg.com/t0147bf05edad4afb11.png)](https://p0.ssl.qhimg.com/t0147bf05edad4afb11.png)

F7一下，发现用到了esp 所以这个混淆的去除不能全给nop掉，因为call 会psuh

[![](https://p1.ssl.qhimg.com/t011fa20072b4a397f8.png)](https://p1.ssl.qhimg.com/t011fa20072b4a397f8.png)

edi就是之前申请的空间地址

[![](https://p3.ssl.qhimg.com/t01a3b20f6f555154ee.png)](https://p3.ssl.qhimg.com/t01a3b20f6f555154ee.png)

继续往后面走就会改变CS为0x33了切64位

[![](https://p4.ssl.qhimg.com/t01c495c5e64e346ee2.png)](https://p4.ssl.qhimg.com/t01c495c5e64e346ee2.png)

为什么0x33会切64位呢？因为保护模式下段选择子可以拆分为

00110 0 11

可以知道RPL=3

TI=0

Index=6

可以去查GDT[6]里面的内容就知道为啥了

切换到64位那么OD就不能调试了，但是可以使用Windbg(x64)的来进行调试

32位和64位的解析是不一样的所以需要打开两份ida看了，还有就是ida其实已经帮我们把混淆识别出来了

[![](https://p5.ssl.qhimg.com/t0181367df718318749.png)](https://p5.ssl.qhimg.com/t0181367df718318749.png)

不过我还是用OD去除混淆了，然后dump下来用ida观察，先看32位的发现先比较了长度和现在比较到了字符串index，因为刚进来所以第一个字符如果不是0x66也就是f的话函数返回0，也就表示失败了。下面的代码切换到64位的0x49e地址

[![](https://p1.ssl.qhimg.com/t013d0a07b122ae6f16.png)](https://p1.ssl.qhimg.com/t013d0a07b122ae6f16.png)

这段代码可以看出有3条路径和0x30比较的是会返回之前的0地址，和0x34比较的会去到0x558的地址，都不是的话就直接抛异常了？？？？(黑人问号这个题是不是出的有点子问题)

[![](https://p5.ssl.qhimg.com/t01f9ffcec9db3e9120.png)](https://p5.ssl.qhimg.com/t01f9ffcec9db3e9120.png)

输入如下图的就会抛异常了，所以我们只需要关注每个块的jz指令即可

[![](https://p5.ssl.qhimg.com/t0124192e9544bb2929.png)](https://p5.ssl.qhimg.com/t0124192e9544bb2929.png)



## 取节点

然后编写了个ida脚本，由于没有考虑到三分支的情况导致出错了，这个脚本也放出来来吧，虽然有问题，主要思路就是判断jz 和mov 指令 ，如果mov 后面跟着的指令不是回去的，或者是走过的块则走下面一个jz

```
import  idc
import  idautils
import  idaapi
flag_map=`{``}`
Is_first=True
eip=0
block_address=0
oldjz_eip=0
while True:
    if GetMnem(eip)=='jz': 
        oldjz_eip=eip
        address=PrevHead(eip)
        c=chr((Byte(address+1))) 
        eip=eip+Byte(eip+1)+2
        if Is_first:
            flag_map[block_address]=c
            Is_first=False
        #print (GetMnem(eip))
        #print("jz:"+hex(eip))    
        while True:
            if GetMnem(eip)=='mov':
                if Byte(eip)==0x36:
                    eip=Dword(eip+5)
                else:
                    eip=Dword(eip+3)
                block_address=eip
                #print("mov:"+hex(block_address))
                if block_address in flag_map.keys():
                    #print ("same")
                    eip=oldjz_eip+1
                    break
                flag_map[block_address]=c
                print c
                break 
            else:
                eip+=1
    else:
        eip+=1

    if eip&gt;=0x30d0:
        break
```

三分支，最后一个比较是回到上一个块，上面个比较对于脚本来说都是可以走的，所以走错了，因为写的逻辑比较简单

因为上一个块连接下一个块，下一个块又能回到上一个块，并且有的还有三个分支，所以应该是图，

结束的节点是0x30d0，搜索这个块可以先搜索retn这个text，再没搜到就搜索C3

取节点代码已经有人写好了参考链接

```
from capstone import *
from struct import *
md_64 = Cs(CS_ARCH_X86, CS_MODE_64)
md_32 = Cs(CS_ARCH_X86, CS_MODE_32)
nodes = `{``}`
with open("code", "rb") as f:
    code = f.read()
def dis32(addr):
    global code, md_32
    tmp = code[addr:addr + 10]
    return md_32.disasm(tmp, addr).__next__()
def dis64(addr):
    global code, md_64
    tmp = code[addr:addr + 10]
    return md_64.disasm(tmp, addr).__next__()
def exp32(addr):
    now = dis32(addr)
    assert now.bytes == b'9\xd9'        #39 d9 开头是32位
    addr += now.size
    now = dis32(addr)
    ret_addr = int(now.op_str, 16)
    ret = dis32(ret_addr)
    assert ret.bytes == b'1\xc0'

    addr += now.size                    # mov al, byte ptr [edx + ecx]
    now = dis32(addr)
    assert now.bytes == b'\x8a\x04\n' 
    node = []
    addr += now.size
    while True:
        if addr == ret_addr:
            break
        now = dis32(addr)
        assert now.mnemonic == 'cmp'
        next_ch = chr(int(now.op_str[4:], 16))

        addr += now.size
        now = dis32(addr)
        jz_addr = int(now.op_str, 16)
        next_addr = unpack("&lt;I", code[jz_addr+15:jz_addr+15+4])[0]
        next = [next_addr, next_ch]
        node.append(next)
        while True:
            addr += now.size
            now = dis32(addr)
            if now.mnemonic == 'cmp' or addr == ret_addr:
                break
    return node
def exp64(addr):
    now = dis64(addr)
    assert now.bytes == b'H9\xd9'  # 48 39 d9 开头表示64位代码块
    addr += now.size
    now = dis64(addr)
    ret_addr = int(now.op_str, 16)
    ret = dis64(ret_addr)
    assert ret.bytes == b'H1\xc0'

    addr += now.size                    # mov al, byte ptr [edx + ecx]
    now = dis64(addr)
    assert now.bytes == b'g\x8a\x04\n'
    node = []
    addr += now.size
    while True:
        if addr == ret_addr:
            break
        now = dis64(addr)
        assert now.mnemonic == 'cmp'
        next_ch = chr(int(now.op_str[4:], 16))

        addr += now.size
        now = dis64(addr)

        jz_addr = int(now.op_str, 16)
        next_addr = unpack("&lt;I", code[jz_addr+21:jz_addr+21+4])[0]
        next = [next_addr, next_ch]
        node.append(next)
        while True:
            addr += now.size
            now = dis64(addr)
            if now.mnemonic == 'cmp' or addr == ret_addr:
                break
    return node
def show(addr, node):
    print("0x%04x -&gt;"%addr, end=' ')
    for i in node:
        print('\''+i[1]+'\'', "0x%04x"%i[0], end=', ')
    print()

def get_graph(addr, switch):
    if addr == 0x30d0:
        return
    global nodes
    if switch == 0:
        node = exp32(addr)
    else:
        node = exp64(addr)
    switch ^= 1
    nodes[addr] = node
    show(addr, node)

    for i in node:
        if i[0] not in nodes.keys():
            get_graph(i[0], switch)
get_graph(0, 0)
```

跑出的结果

```
0x0000 -&gt; 'f' 0x049e, 
0x049e -&gt; '0' 0x0000, '4' 0x0558, 
0x0558 -&gt; 'f' 0x09cc, '9' 0x049e,
0x09cc -&gt; '2' 0x0558, 'c' 0x098a,
0x098a -&gt; 'e' 0x0e60, '6' 0x09cc,
0x0e60 -&gt; '8' 0x098a, '9' 0x0f1a, 
0x0f1a -&gt; '5' 0x1372, 'f' 0x0e60,
0x1372 -&gt; 'e' 0x0f1a, 'b' 0x192c,
0x192c -&gt; 'c' 0x1372, '6' 0x1838,
0x1838 -&gt; '0' 0x134c, '3' 0x1dd4, '5' 0x192c, 
0x134c -&gt; '7' 0x1838,
0x1dd4 -&gt; '2' 0x1838, 'f' 0x22c0,
0x22c0 -&gt; 'a' 0x1dd4, '5' 0x27ac,
0x27ac -&gt; '2' 0x22c0, '7' 0x2c02, 
0x2c02 -&gt; 'f' 0x27ac, '1' 0x2cbc,
0x2cbc -&gt; '8' 0x2cfe, '9' 0x2c02,
0x2cfe -&gt; '7' 0x2db8, '0' 0x2cbc,
0x2db8 -&gt; 'c' 0x2dfa, 'b' 0x2cfe,
0x2dfa -&gt; '9' 0x2eb4, '8' 0x2db8, 
0x2eb4 -&gt; '4' 0x29b4, 'a' 0x2dfa,
0x29b4 -&gt; '5' 0x2eb4, '2' 0x2a6e,
0x2a6e -&gt; '4' 0x25b4, 'a' 0x29b4,
0x25b4 -&gt; '7' 0x2a6e, 'a' 0x266e,
0x266e -&gt; 'e' 0x210a, '5' 0x25b4,
0x210a -&gt; '8' 0x266e, '0' 0x21c4, 
0x21c4 -&gt; '6' 0x1cbc, 'b' 0x210a,
0x1cbc -&gt; 'e' 0x21c4, 'c' 0x1d76,
0x1d76 -&gt; '8' 0x177e, 'f' 0x2206, 'e' 0x1cbc,
0x177e -&gt; '0' 0x130a, '2' 0x1d76, 
0x130a -&gt; '4' 0x177e, 'd' 0x1250,
0x1250 -&gt; '3' 0x173c, '0' 0x130a, 
0x173c -&gt; '1' 0x1250, '2' 0x1682,
0x1682 -&gt; 'a' 0x120e, '3' 0x173c,
0x120e -&gt; '9' 0x1682, 'e' 0x1154,
0x1154 -&gt; 'b' 0x1640, 'c' 0x120e,
0x1640 -&gt; '4' 0x1154, 'e' 0x1ba2,
0x1ba2 -&gt; 'f' 0x1640, '9' 0x20c8, '2' 0x1c96,
0x20c8 -&gt; '5' 0x1ba2, '1' 0x200e,
0x200e -&gt; '8' 0x2572, 'd' 0x20c8,
0x2572 -&gt; '0' 0x200e, '5' 0x24b8, 
0x24b8 -&gt; 'd' 0x2972, '5' 0x2572,
0x2972 -&gt; 'e' 0x24b8, 'c' 0x28b8,
0x28b8 -&gt; 'e' 0x2476, 'd' 0x2972,
0x2476 -&gt; 'c' 0x1f2e, '7' 0x28b8,
0x1f2e -&gt; '7' 0x2476, 'e' 0x1ed0,
0x1ed0 -&gt; '2' 0x196e, 'd' 0x1f2e, '6' 0x1e16,
0x196e -&gt; '3' 0x142c, '2' 0x1ed0,
0x142c -&gt; '9' 0x196e, 'f' 0x146e,
0x146e -&gt; '1' 0x1016, '7' 0x142c, 
0x1016 -&gt; '9' 0x146e, '5' 0x0f5c,
0x0f5c -&gt; 'c' 0x0a86, 'f' 0x1016,
0x0a86 -&gt; '1' 0x059a, '5' 0x0f5c,
0x059a -&gt; '3' 0x00ae, 'a' 0x0a86,
0x00ae -&gt; 'c' 0x059a, '6' 0x010c, '7' 0x0026, 
0x010c -&gt; 'b' 0x0654, 'e' 0x00ae,
0x0654 -&gt; '9' 0x010c, 'c' 0x0696,
0x0696 -&gt; '7' 0x01c6, '6' 0x0654,
0x01c6 -&gt; '0' 0x0696, 'f' 0x0208,
0x0208 -&gt; 'b' 0x0750, 'c' 0x01c6,
0x0750 -&gt; 'd' 0x0208, 'c' 0x0792,
0x0792 -&gt; '5' 0x02c2, '9' 0x0750,
0x02c2 -&gt; '3' 0x0792, 'c' 0x0304,
0x0304 -&gt; '3' 0x084c, 'd' 0x02c2, 
0x084c -&gt; 'd' 0x0304, '9' 0x088e,
0x088e -&gt; 'e' 0x0d48, '2' 0x084c,
0x0d48 -&gt; 'd' 0x088e, 'b' 0x0da6, '3' 0x0c8e,
0x0da6 -&gt; '0' 0x0948, '5' 0x0d48,
0x0948 -&gt; '2' 0x03e4, 'c' 0x0da6,
0x03e4 -&gt; 'f' 0x0948, '1' 0x03be, 
0x03be -&gt; '5' 0x03e4,
0x0c8e -&gt; '9' 0x0d48, '5' 0x0c4c,
0x0c4c -&gt; 'c' 0x0c8e, '9' 0x0b92,
0x0b92 -&gt; '4' 0x1112, '3' 0x0c4c,
0x1112 -&gt; '9' 0x0b92, 'f' 0x1586,
0x1586 -&gt; '2' 0x1112, '9' 0x1528,
0x1528 -&gt; '0' 0x1058, 'e' 0x1a4e, '5' 0x1586,
0x1058 -&gt; 'b' 0x0b50, 'e' 0x1528,
0x0b50 -&gt; 'b' 0x1058, '8' 0x0ac8,
0x0ac8 -&gt; 'd' 0x0b50,
0x1a4e -&gt; '8' 0x1528, '7' 0x1fe8, '0' 0x1b7c, '1' 0x1a28, 
0x1fe8 -&gt; '3' 0x1a4e,
0x1b7c -&gt; '9' 0x1a4e,
0x1a28 -&gt; '0' 0x1a4e,
0x0026 -&gt; '3' 0x00ae,
0x1e16 -&gt; 'b' 0x237a, 'c' 0x1ed0,
0x237a -&gt; '2' 0x1e16, '5' 0x23bc,
0x23bc -&gt; '9' 0x2876, '6' 0x237a, 
0x2876 -&gt; '2' 0x23bc, 'e' 0x27ee,
0x27ee -&gt; '3' 0x2876,
0x1c96 -&gt; 'a' 0x1ba2,
0x2206 -&gt; 'e' 0x1d76, '1' 0x276a,
0x276a -&gt; '9' 0x2206, 'a' 0x26b0,
0x26b0 -&gt; '8' 0x2b38, 'e' 0x276a,
0x27ee -&gt; '3' 0x2876,
0x1c96 -&gt; 'a' 0x1ba2,
0x2206 -&gt; 'e' 0x1d76, '1' 0x276a,
0x276a -&gt; '9' 0x2206, 'a' 0x26b0,
0x26b0 -&gt; '8' 0x2b38, 'e' 0x276a,
0x2b38 -&gt; '7' 0x26b0, '6' 0x2fdc,
0x2fdc -&gt; 'a' 0x2b38, 'f' 0x30d0, 'c' 0x2f7e,
0x2f7e -&gt; '3' 0x2ab0, '5' 0x2fdc, '9' 0x2ef6,
0x2ab0 -&gt; '5' 0x2f7e,
0x2ef6 -&gt; '8' 0x2f7e,
```



## 图搜算法

接下来就是图搜索算法了，需要找到一条从0到0x30d0的路径。

```
def dfs(addr, flag, path):
    if addr == 0x30d0:
        print("found!")
        print("npointer`{`"+flag+"`}`")
        return
    node = nodes[addr]
    for i in node:
        if i[0] not in path:
            get_path(i[0], flag+i[1], path+[i[0]])
dfs(0, "", [])
```

输出结果

```
found!
npointer`{`f4fce95b63f57187c9424ae06cf1a86f`}`
```

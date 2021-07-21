> 原文链接: https://www.anquanke.com//post/id/221905 


# 深入 FRIDA-DEXDump 中的矛与盾


                                阅读量   
                                **239876**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t01cede8fb427d076ed.png)](https://p3.ssl.qhimg.com/t01cede8fb427d076ed.png)



一转眼， 已经从发布 [FRIDA-DEXDump](https://github.com/hluwa/FRIDA-DEXDump) 的年初到了炒冷饭的年末。

2020 是格外梦幻的一年，有灾难，有牛市，有大选，还有 1K+ Star。

感谢 NowSecure，感谢大胡子，感谢 Frida，感谢炫酷的 Banner。

当然，FRIDA-DEXDump 并不是个花瓶，在过去的 10 个月中，我迭代了几次核心代码，目前已经基本实现对抗 99% 基于文件粒度的保护手段。(假的，我就没试过几个样本

但是，因为发脚本的时候对具体的原理只有一笔带过，所以可能大部分人还对其的理解还只停留在搜索 `DEX.035` 上面，所以我决定炒一下冷饭（免得自己过几天就忘了），同时也希望给对抗双方能有一些启发，即便这已经不是主流的研究方向。



## 古老的技法

目前很多其他脱壳机的原理是通过拦截系统加载代码的链路上的一些函数，通过函数参数得到一些结构体，并从中获取 `DEX` 的内存地址或其他相关信息。这里面有一些缺点：**需要适配不同的系统，函数名、函数参数都有可能不同，并且很多情景下对注入拦截的时机有要求**，毕竟文件只需要加载一次， 错过这个村儿就没这个店儿了。

FRIDA-DEXDump 则不同，其是纯粹的利用特征从内存中检索已经加载的 `DEX` 文件，而不需要拦截任何的函数。

实际上这是一项十分古老且通俗的技法。

搜索 `DEX.035` 确实是在内存中寻找 `DEX` 文件最常规有效的方式。但，代码保护总是不能走常规的道路。

如果看过项目的 README, 大概率都知道 FRIDA-DEXDump 支持一个特性：支持搜索没有文件头的 `DEX` 文件，这是如何实现的？



## 雾里看花

首先了解一下 DEX 文件头的格式:

```
struct header_item `{`
    uchar[8] magic &lt;comment="Magic value"&gt;;
    uint checksum &lt;format=hex, comment="Alder32 checksum of rest of file"&gt;;
    uchar[20] signature &lt;comment="SHA-1 signature of rest of file"&gt;;
    uint file_size &lt;comment="File size in bytes"&gt;;
    uint header_size &lt;comment="Header size in bytes"&gt;;
    uint endian_tag &lt;format=hex, comment="Endianness tag"&gt;;
    uint link_size &lt;comment="Size of link section"&gt;;
    uint link_off &lt;comment="File offset of link section"&gt;;
    uint map_off &lt;comment="File offset of map list"&gt;;
    uint string_ids_size &lt;comment="Count of strings in the string ID list"&gt;;
    uint string_ids_off &lt;comment="File offset of string ID list"&gt;;
    uint type_ids_size &lt;comment="Count of types in the type ID list"&gt;;
    uint type_ids_off &lt;comment="File offset of type ID list"&gt;;
    uint proto_ids_size &lt;comment="Count of items in the method prototype ID list"&gt;;
    uint proto_ids_off &lt;comment="File offset of method prototype ID list"&gt;;
    uint field_ids_size &lt;comment="Count of items in the field ID list"&gt;;
    uint field_ids_off &lt;comment="File offset of field ID list"&gt;;
    uint method_ids_size &lt;comment="Count of items in the method ID list"&gt;;
    uint method_ids_off &lt;comment="File offset of method ID list"&gt;;
    uint class_defs_size &lt;comment="Count of items in the class definitions list"&gt;;
    uint class_defs_off &lt;comment="File offset of class definitions list"&gt;;
    uint data_size &lt;comment="Size of data section in bytes"&gt;;
    uint data_off &lt;comment="File offset of data section"&gt;;
`}`;
```

在最原始的代码中，实现部分的代码是这样的：

```
Process.enumerateRanges('r--').forEach(function (range) `{`
    if (
      range.size &gt;= 0x60
      &amp;&amp; range.base.readCString(4) != "dex\n"
      &amp;&amp; range.base.add(0x20).readInt() &lt;= range.size //file_size
      &amp;&amp; range.base.add(0x34).readInt() &lt; range.size //map_off
      &amp;&amp; range.base.add(0x3C).readInt() == 112 //string_id_off
    ) `{`
      result.push(`{`"addr": range.base,"size": range.base.add(0x20).readInt()`}`);
`}`
```

简单来说，就是先把一块不知道是不是 `DEX` 的内存当作 `DEX` 看，然后通过文件格式来进行校验，增强可信度。

逐行解释一下代码：
<li>
`Process.enumerateRanges('r--')` 这是用于遍历当前进程中所有可以读的内存段，毕竟不能读的内存区域是不能被 VM 执行的 (Native 可以)。 想必不难理解。</li>
<li>
`range.size &gt;= 0x60` 这段内存必须大于 `0x60`，因为 `DEX` 文件头的大小是 `0x70`，要是头都放不下，就更不要说其他的了。（至于为啥写的 0x60 我也忘了</li>
<li>
`range.base.readCString(4) != "dex\n"`， 从这段内存开始地方的读 4 个字节的字符串，如果没有 dex 的魔术头，再接着往下看。</li>
<li>
`range.base.add(0x20).readInt() &lt;= range.size`， `DEX` 文件头 `+0x20` 的位置，是 `file_size`， 也就是这个 `DEX` 文件的总大小，如果这段内存不够这么大，那么显然也是存不下这个文件的，那就可以 pass 了。</li>
<li>
`range.base.add(0x34).readInt() &lt; range.size` ，`+0x34` 是 `map_off` ，也就是 `map` 段的偏移位置，一般情况下 `map` 段都是在 `DEX` 文件的最末尾，与 `file_size` 同理。</li>
<li>
`range.base.add(0x3C).readInt() == 112`，`+0x3C` 是 `string_ids_off`， 也就是 `string_ids` 段的偏移位置，而这个段一般是紧随于 `DEX` 头后面，而 `DEX` 头的大小是 `0x70 = 112`，所以这个一般来说也是固定的。</li>
通过这么几个校验之后，我们已经可以把这块内存当成是一个 `DEX` 文件来 dump 了。

这其实有一个问题，就是只有当 `DEX` 加载于段头的时候才能匹配出来，即便这个内存段在开头加上一个字节都不行。因为若是进行全局扫描，那么条件将会变得十分不可靠，可能会匹配出很多的 `112`。 这个问题先放一边，下面一起解决。



## 探囊取物

但后来我发现一件事情：内存中的 `DEX Header` 并不只有 `magic` 可以抹掉，还有另一个运行时无关但对我们至关重要的字段：`file_size`，也就是文件的大小。

文件大小被抹掉，意味着我们无法知道想要 dump 的区域大小是多少。

于是我又使用了一种新的方案： 通过 `map_off` 找到 `DEX` 的 `map_list`， 通过解析它，并得到类型为 `TYPE_MAP_LIST` 的条目。理论上讲，这个条目里面的索引值应该要与 `map_off` 一致，那么通过校验这两个地方，就可以实现一个更加精确的验证方案。 验证代码如下：

```
function verify_by_maps(dexptr, mapsptr) `{`
    var maps_offset = dexptr.add(0x34).readUInt();
    var maps_size = mapsptr.readUInt();
    for (var i = 0; i &lt; maps_size; i++) `{`
        var item_type = mapsptr.add(4 + i * 0xC).readU16();
        if (item_type === 4096) `{` //4096 == TYPE_MAP_LIST
            var item_offset = mapsptr.add(4 + i * 0xC + 8).readUInt();
            if (maps_offset === item_offset) `{`
                return true;
            `}`
        `}`
    `}`
    return false;
`}`
```

然后再计算 `map_list` 结束的位置:

```
function get_maps_end(maps, range_base, range_end) `{`
    var maps_size = maps.readUInt();
    if (maps_size &lt; 2 || maps_size &gt; 50) `{`
        return null;
    `}`
    var maps_end = maps.add(maps_size * 0xC + 4);
    if (maps_end &lt; range_base || maps_end &gt; range_end) `{`
        return null;
    `}`

    return maps_end;
`}`
```

最后通过减掉起始地址，就可以得到真正的文件大小了:

```
function get_dex_real_size(dexptr, range_base, range_end) `{`
    var dex_size = dexptr.add(0x20).readUInt();

    var maps_address = get_maps_address(dexptr, range_base, range_end);
    if (!maps_address) `{`
        return dex_size;
    `}`

    var maps_end = get_maps_end(maps_address, range_base, range_end);
    if (!maps_end) `{`
        return dex_size;
    `}`

    return maps_end - dexptr
`}`
```

在这种方案中，仅需要 `Dex Header` 存在 `map_off` 即可。不仅如此，还解决了上面的一个问题，因为有了这个验证方案，我们可以肆意妄为的在内存中搜索 `112` 了，搜索到了之后再校验一下 `maps` 是否正常。不管藏在中间还是结尾，都可以找出来。不过在 `FRIDA-DEXdump` 中，需要使用 `-d` 开启深度搜索模式才会这么暴力搜索哦。



## 聚沙成塔

有些加固厂商还使用了 “DEX 文件打散” 的技术，所谓的文件打散就是将 `DEX` 文件的各个分区抽取出来分散存放，令内存中的 `DEX` 文件不连续。

理论上很美好，但实际上很多经过所谓的打散之后，所有的分区实际上都还在同一个内存段里，当然这也很好理解，如果每次都分配一个新的内存段来存放不同的分区，那就需要动态修复索引了，可能会比较麻烦。

当然这对 `FRIDA-DEXDump` 也是有影响的，因为文件打散之后数据分区往往就不再会在 `file_size` 或者所谓的真实文件大小范围内了，所以 `dump` 的时候也就拿不到真实的数据。

但是因为所有的分区依然在同一个内存段里，所以只要在验证完 maps 之后，直接 `dump` 至内存段末尾即可。

因为 `DEX` 文件格式中对各个分区的索引都是相对偏移，所以对于大部分常用的反编译器 ，只需要简单的修复一下文件大小就可以打开了，毕竟运行时的索引肯定都是正确的。 同样的，`-d` 也会开启此功能。

## …

经常有人跑来提问说为什么用不了，这种问题我大概率都是不理会的，因为报错信息一看肯定要么是 `frida` 连不上，要么是注入不进去。

只能说工具不是万能的，`FRIDA-DEXDump` 本身是一个没什么技术含量的小脚本，如何正确的使用完全靠个人。

你们知道这个小破脚本有哪些使用的小技巧吗？ 可以通过评论或者”虎克老湿基”公众号告诉我喔 ~

